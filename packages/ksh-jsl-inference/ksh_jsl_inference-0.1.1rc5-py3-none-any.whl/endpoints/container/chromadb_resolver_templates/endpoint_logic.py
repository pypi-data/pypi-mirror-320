"""
A skeleton of the file that needs to be implemented for each model endpoints.
Use this file only as a template
"""

import json
import pandas as pd
from typing import Dict, List
from pyspark.sql import DataFrame as SparkDataFrame
from typing import Any, Dict, List, Union
from pydantic import BaseModel, validator
from pandas import DataFrame as PandasDataFrame
from pyspark.sql import functions as F

from custom_logging import logger
from model_loader import light_pipeline, pretrained_pipeline, spark, local_db


class FormatInput(BaseModel):
    text: Union[str, List[str]]

    @validator("text")
    def validate_text_format(cls, v: Any) -> Union[str, List[str]]:
        if isinstance(v, str):
            return [v]
        elif isinstance(v, list):
            if not all(isinstance(item, str) for item in v):
                raise ValueError(
                    "Invalid input format. All elements in 'text' list must be strings."
                )
            return v
        else:
            raise ValueError(
                "Invalid input format. 'text' field must be a string or a list of strings."
            )


def prepare_data(texts: List[str]) -> SparkDataFrame:
    logger.debug("Preparing the Spark DataFrame")
    indexed_text = [(i, t) for i, t in enumerate(texts)]
    df = spark.createDataFrame(indexed_text, ["index", "text"])
    return df.repartition(1000)


def get_predictions_from_light_pipeline(texts: List[str]) -> PandasDataFrame:
    logger.debug(f"Processing {len(texts)} texts with Light Pipeline")
    results = light_pipeline.fullAnnotate(texts)

    all_predictions = [
        {
            "index": idx,
            "begin": ner_chunk.begin,
            "end": ner_chunk.end,
            "ner_chunk": ner_chunk.result,
            "ner_label": ner_chunk.metadata["entity"],
            "ner_confidence": ner_chunk.metadata["confidence"],
        }
        for idx, prediction in enumerate(results)
        for ner_chunk in prediction.get("ner_chunk", [])
    ]

    return pd.DataFrame(
        all_predictions,
        columns=["index", "begin", "end", "ner_chunk", "ner_label", "ner_confidence"],
    )


def get_predictions_from_pretrained_pipeline(texts: List[str]) -> PandasDataFrame:
    logger.debug(f"Processing {len(texts)} texts with Pretrained Pipeline")
    input_df = prepare_data(texts)
    predictions_df = pretrained_pipeline.transform(input_df).cache()
    sorted_df = predictions_df.orderBy("index")

    return (
        sorted_df.select(
            "index",
            F.explode(
                F.arrays_zip(
                    sorted_df.ner_chunk.begin,
                    sorted_df.ner_chunk.end,
                    sorted_df.ner_chunk.result,
                    sorted_df.ner_chunk.metadata,
                )
            ).alias("cols"),
        )
        .select(
            "index",
            F.expr("cols['0']").alias("begin"),
            F.expr("cols['1']").alias("end"),
            F.expr("cols['2']").alias("ner_chunk"),
            F.expr("cols['3']['entity']").alias("ner_label"),
            F.expr("cols['3']['confidence']").alias("ner_confidence"),
        )
        .toPandas()
    )


def get_resolver_results(
    chunk_list: List[str], k=100, top_results=5
) -> PandasDataFrame:
    logger.debug(f"Processing {len(chunk_list)} chunks for resolver results")

    resolver_result_df = pd.DataFrame({"query": []})

    for query in chunk_list:
        res = local_db.similarity_search_with_relevance_scores(query=query, k=k)[
            :top_results
        ]
        # Get all metadata keys from the first document in the first result.
        all_keys = list(res[0][0].metadata.keys())

        # Create a dictionary to store metadata values for each key.
        metadata_lists = {key: [] for key in all_keys}

        # Iterate through each document and its score in the results.
        for doc, _ in res:
            # For each metadata key:
            for key in all_keys:
                metadata_lists[key].append(doc.metadata.get(key, None))

            # Create a dictionary where keys are metadata keys and values are lists of metadata values.
            res_dict = {key: [value] for key, value in metadata_lists.items()}

            # Add a new key "all_resolutions" containing a list of the page content for all results.
            res_dict["all_resolutions"] = [[i[0].page_content for i in res]]

            # Add a new key "all_score" containing a list of the scores for all results.
            res_dict["all_score"] = [[i[1] for i in res]]

            # Create a Pandas DataFrame from the dictionary.
            tmp_df = pd.DataFrame(res_dict)

            # Rename the "concept_code" column to "all_codes".
            tmp_df.rename(columns={"concept_code": "all_codes"}, inplace=True)

            # Create a "concept_code" column from the first element of "all_codes".
            tmp_df["concept_code"] = tmp_df["all_codes"].apply(lambda x: x[0])

            # Create a "resolution" column from the first element of "all_resolutions".
            tmp_df["resolution"] = tmp_df["all_resolutions"].apply(lambda x: x[0])

            # Create a "score" column from the first element of "all_score".
            tmp_df["score"] = tmp_df["all_score"].apply(lambda x: x[0])

            # Reorder columns
            cols = tmp_df.columns.to_list()
            cols.remove("resolution")
            cols.remove("concept_code")
            cols.remove("score")
            tmp_df = tmp_df[["concept_code", "resolution", "score"] + cols]

        resolver_result_df = pd.concat([resolver_result_df, tmp_df])

    resolver_result_df["query"] = chunk_list
    resolver_result_df.reset_index(drop=True, inplace=True)
    return resolver_result_df


def get_predictions(texts: List[str]) -> List:
    if len(texts) < 20:
        ner_df = get_predictions_from_light_pipeline(texts)
    else:
        ner_df = get_predictions_from_pretrained_pipeline(texts)

    ner_df["lower_cased_ner_chunk"] = ner_df.ner_chunk.str.lower()
    chunk_list = list(set(ner_df.lower_cased_ner_chunk))

    resolver_df = get_resolver_results(chunk_list)

    ner_df["lower_cased_ner_chunk"] = ner_df["lower_cased_ner_chunk"].astype(str)
    resolver_df["query"] = resolver_df["query"].astype(str)
    result_df = pd.merge(
        ner_df, resolver_df, left_on="lower_cased_ner_chunk", right_on="query"
    )

    result_df.drop(["lower_cased_ner_chunk", "query"], axis=1, inplace=True)

    grouped = result_df.groupby("index")
    output_list = []

    for i in range(len(texts)):
        if i in grouped.groups:
            predictions = [
                {k: v for k, v in row.items() if k != "index"}
                for _, row in grouped.get_group(i).iterrows()
            ]
            output_list.append(predictions)
        else:
            output_list.append([])

    return output_list


def get_predictions_from_json_data(input_data: str) -> Dict:
    input_json = json.loads(input_data)
    input_data_obj = FormatInput(**input_json)
    predictions = get_predictions(input_data_obj.text)
    return {
        "consumed_units": len(input_data_obj.text),
        "predictions": predictions,
    }


def get_predictions_from_jsonlines_data(input_data: str) -> Dict:
    input_texts = []
    for line_number, line in enumerate(input_data.splitlines()):
        try:
            json_data = json.loads(line)
            input_obj = FormatInput(**json_data)
            input_texts.extend(input_obj.text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON line at line {line_number}: {line}") from e
        except Exception as e:
            raise ValueError(
                f"Error processing JSON line at line {line_number}: {line} - {str(e)}"
            ) from e

    predictions = get_predictions(input_texts)

    return {
        "consumed_units": len(input_texts),
        "predictions": predictions,
    }


def get_json_response(predictions: List[list], **kwargs):
    return json.dumps({"predictions": predictions})


def get_jsonlines_response(predictions: List[list], **kwargs):
    return "\n".join([json.dumps({"predictions": pred}) for pred in predictions])


def get_predictions_for_snowflake(data: dict) -> Dict:
    input_texts = [i[1] for i in data["data"]]
    predictions = get_predictions(input_texts)
    return {"predictions": predictions}


def get_response_for_snowflake(predictions, **kwargs):
    return [[idx, pred] for idx, pred in enumerate(predictions)]
