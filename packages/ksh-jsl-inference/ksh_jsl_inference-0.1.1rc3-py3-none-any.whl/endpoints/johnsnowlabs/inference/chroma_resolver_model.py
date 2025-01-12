from typing import List, Dict

from endpoints.schema import Schema
from endpoints.log_utils import logger

from pyspark.sql.dataframe import DataFrame
from endpoints.johnsnowlabs.inference.medical_nlp_model import MedicalNlpInferenceModel


class ChromaDbResolverInferenceModel(MedicalNlpInferenceModel):
    from pyspark.sql import functions as F
    import pandas as pd

    def __init__(self):
        super().__init__()
        self._output = Schema(field="predictions", typing=List)
        self._local_db = None

    def get_python_requirements(self) -> List[str]:
        return [
            "langchain==0.2.7",
            "langchain-community==0.2.7",
            "sentence-transformers==3.2.1",
            "Chroma==0.2.0",
            "chromadb==0.5.23",
            "pysqlite3-binary==0.5.3",
        ]

    @property
    def local_db(self):
        if not self._local_db:
            from endpoints.johnsnowlabs.chromadb_resolver_model_loader import local_db

            self._local_db = local_db
        return self._local_db

    @property
    def spark(self):
        if not self._spark:
            from endpoints.johnsnowlabs.chromadb_resolver_model_loader import spark

            self._spark = spark
        return self._spark

    @property
    def light_pipeline(self):
        if not self._light_pipeline:
            from endpoints.johnsnowlabs.chromadb_resolver_model_loader import (
                light_pipeline,
            )

            self._light_pipeline = light_pipeline
        return self._light_pipeline

    def process_light_pipeline_results(
        self, inputs: List[str], results: List, params: Dict
    ) -> List:
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
        df = self.pd.DataFrame(
            all_predictions,
            columns=[
                "index",
                "begin",
                "end",
                "ner_chunk",
                "ner_label",
                "ner_confidence",
            ],
        )

        return self._post_process(inputs, df)

    def process_pretrained_pipeline_results(
        self, inputs: List[str], results: DataFrame, params: Dict
    ) -> List:
        df = (
            results.select(
                "index",
                self.F.explode(
                    self.F.arrays_zip(
                        results.ner_chunk.begin,
                        results.ner_chunk.end,
                        results.ner_chunk.result,
                        results.ner_chunk.metadata,
                    )
                ).alias("cols"),
            )
            .select(
                "index",
                self.F.expr("cols['0']").alias("begin"),
                self.F.expr("cols['1']").alias("end"),
                self.F.expr("cols['2']").alias("ner_chunk"),
                self.F.expr("cols['3']['entity']").alias("ner_label"),
                self.F.expr("cols['3']['confidence']").alias("ner_confidence"),
            )
            .toPandas()
        )

        return self._post_process(inputs, df)

    def _get_resolver_results(
        self, chunk_list: List[str], k=100, top_results=5
    ) -> pd.DataFrame:
        logger.debug(f"Processing {len(chunk_list)} chunks for resolver results")

        resolver_result_df = self.pd.DataFrame({"query": []})

        for query in chunk_list:
            res = self.local_db.similarity_search_with_relevance_scores(
                query=query, k=k
            )[:top_results]
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
                tmp_df = self.pd.DataFrame(res_dict)

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

            resolver_result_df = self.pd.concat([resolver_result_df, tmp_df])

        resolver_result_df["query"] = chunk_list
        resolver_result_df.reset_index(drop=True, inplace=True)
        return resolver_result_df

    def _post_process(self, inputs: List, ner_df: pd.DataFrame) -> List:

        ner_df["lower_cased_ner_chunks"] = ner_df.ner_chunk.str.lower()
        chunk_list = list(set(ner_df.lower_cased_ner_chunks))

        resolver_df = self._get_resolver_results(chunk_list)

        ner_df["lower_cased_ner_chunks"] = ner_df["lower_cased_ner_chunks"].astype(str)
        resolver_df["query"] = resolver_df["query"].astype(str)
        result_df = self.pd.merge(
            ner_df, resolver_df, left_on="lower_cased_ner_chunks", right_on="query"
        )

        result_df.drop(["lower_cased_ner_chunks", "query"], axis=1, inplace=True)

        grouped = result_df.groupby("index")
        output_list = []

        for i in range(len(inputs)):
            if i in grouped.groups:
                predictions = [
                    {k: v for k, v in row.items() if k != "index"}
                    for _, row in grouped.get_group(i).iterrows()
                ]
                output_list.append(predictions)
            else:
                output_list.append([])

        return output_list
