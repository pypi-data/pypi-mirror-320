import argparse
import os
import shutil

from johnsnowlabs import nlp

HARDWARE_TARGET = os.environ.get("HARDWARE_TARGET", "cpu")
MODEL_LOCATION = "/opt/ml/model"


nlp.install(
    json_license_path="/run/secrets/license",
    browser_login=False,
    force_browser=False,
    hardware_platform=HARDWARE_TARGET,
)

spark = nlp.start()
spark.sparkContext.setLogLevel("ERROR")

from sparknlp.annotator import *
from sparknlp_jsl.annotator import *
from pyspark.ml import Pipeline


def t_or_f(arg):
    ua = str(arg).upper()
    if "TRUE".startswith(ua):
        return True
    elif "FALSE".startswith(ua):
        return False
    else:
        return True


def get_ner_stages(concept, spark):
    """
    Builds a pipeline of stages for Named Entity Recognition (NER) based on the given concept.

    Args:
        concept (str): The medical coding system or concept (e.g., "icd10cm", "mesh").

    Returns:
        list: A list of Spark NLP pipeline stages for NER.
    """
    # Dictionary storing NER model configurations for different concepts
    vdb_ner_models = {
        "icd10cm": {
            "ner_clinical": ["PROBLEM"],
            "ner_jsl": [
                "CEREBROVASCULAR_DISEASE",
                "COMMUNICABLE_DISEASE",
                "DIABETES",
                "DISEASE_SYNDROME_DISORDER",
                "EKG_FINDINGS",
                "HEART_DISEASE",
                "HYPERLIPIDEMIA",
                "HYPERTENSION",
                "IMAGINGFINDINGS",
                "INJURY_OR_POISONING",
                "KIDNEY_DISEASE",
                "OBESITY",
                "ONCOLOGICAL",
                "OVERWEIGHT",
                "PREGNANCY",
                "PSYCHOLOGICAL_CONDITION",
                "SYMPTOM",
                "VS_FINDING",
            ],
        },
        "mesh": {"ner_clinical": []},
        "atc": {"ner_posology": ["DRUG"]},
        "cpt": {
            "ner_jsl": ["PROCEDURE"],
            "ner_measurements_clinical": ["MEASUREMENTS"],
        },
        "hcc": {
            "ner_clinical": ["PROBLEM"],
            "ner_jsl": [
                "CEREBROVASCULAR_DISEASE",
                "COMMUNICABLE_DISEASE",
                "DIABETES",
                "DISEASE_SYNDROME_DISORDER",
                "EKG_FINDINGS",
                "HEART_DISEASE",
                "HYPERLIPIDEMIA",
                "HYPERTENSION",
                "IMAGINGFINDINGS",
                "INJURY_OR_POISONING",
                "KIDNEY_DISEASE",
                "OBESITY",
                "ONCOLOGICAL",
                "OVERWEIGHT",
                "PREGNANCY",
                "PSYCHOLOGICAL_CONDITION",
                "SYMPTOM",
                "VS_FINDING",
            ],
        },
        "ndc": {"ner_posology_greedy": ["DRUG"]},
        "ncit": {
            "ner_oncology": [
                "ADENOPATHY",
                "BIOMARKER",
                "BIOMARKER_RESULT",
                "CANCER_DX",
                "CANCER_SCORE",
                "CANCER_SURGERY",
                "CHEMOTHERAPY",
                "CYCLE_COUNT",
                "CYCLE_DAY",
                "CYCLE_NUMBER",
                "DIRECTION",
                "DURATION",
                "FREQUENCY",
                "GRADE",
                "HISTOLOGICAL_TYPE",
                "HORMONAL_THERAPY",
                "IMAGING_TEST",
                "IMMUNOTHERAPY",
                "INVASION",
                "LINE_OF_THERAPY",
                "METASTASIS",
                "ONCOGENE",
                "PATHOLOGY_RESULT",
                "PATHOLOGY_TEST",
                "PERFORMANCE_STATUS",
                "RADIATION_DOSE",
                "RADIOTHERAPY",
                "RESPONSE_TO_TREATMENT",
                "ROUTE",
                "SITE_BONE",
                "SITE_BRAIN",
                "SITE_BREAST",
                "SITE_LIVER",
                "SITE_LUNG",
                "SITE_LYMPH_NODE",
                "SITE_OTHER_BODY_PART",
                "STAGING",
                "TARGETED_THERAPY",
                "TUMOR_FINDING",
                "UNSPECIFIC_THERAPY",
            ]
        },
        "hcpcs": {"ner_jsl": ["PROCEDURE"], "ner_clinical": ["TREATMENT"]},
        "hgnc": {"ner_human_phenotype_gene_clinical": ["GENE"]},
        "meddra_llt": {
            "ner_jsl": [
                "PROCEDURE",
                "KIDNEY_DISEASE",
                "CEREBROVASCULAR_DISEASE",
                "HEART_DISEASE",
                "DISEASE_SYNDROME_DISORDER",
                "IMAGINGFINDINGS",
                "SYMPTOM",
                "VS_FINDING",
                "EKG_FINDINGS",
                "COMMUNICABLE_DISEASE",
                "SUBSTANCE",
                "INTERNAL_ORGAN_OR_COMPONENT",
                "EXTERNAL_BODY_PART_OR_REGION",
                "MODIFIER",
                "TRIGLYCERIDES",
                "ALCOHOL",
                "SMOKING",
                "PREGNANCY",
                "HYPERTENSION",
                "OBESITY",
                "INJURY_OR_POISONING",
                "TEST",
                "HYPERLIPIDEMIA",
                "BMI",
                "ONCOLOGICAL",
                "PSYCHOLOGICAL_CONDITION",
                "LDL",
                "DIABETES",
            ],
            "ner_clinical_large": ["PROBLEM"],
        },
        "meddra_pt": {
            "ner_jsl": [
                "PROCEDURE",
                "KIDNEY_DISEASE",
                "CEREBROVASCULAR_DISEASE",
                "HEART_DISEASE",
                "DISEASE_SYNDROME_DISORDER",
                "IMAGINGFINDINGS",
                "SYMPTOM",
                "VS_FINDING",
                "EKG_FINDINGS",
                "COMMUNICABLE_DISEASE",
                "SUBSTANCE",
                "INTERNAL_ORGAN_OR_COMPONENT",
                "EXTERNAL_BODY_PART_OR_REGION",
                "MODIFIER",
                "TRIGLYCERIDES",
                "ALCOHOL",
                "SMOKING",
                "PREGNANCY",
                "HYPERTENSION",
                "OBESITY",
                "INJURY_OR_POISONING",
                "TEST",
                "HYPERLIPIDEMIA",
                "BMI",
                "ONCOLOGICAL",
                "PSYCHOLOGICAL_CONDITION",
                "LDL",
                "DIABETES",
            ],
            "ner_clinical_large": ["PROBLEM"],
        },
        "rxnorm": {"ner_posology_greedy": ["DRUG"], "ner_jsl_greedy": ["DRUG"]},
        "icd10pcs": {"ner_clinical": ["TREATMENT"], "ner_jsl": ["PROCEDURE"]},
        "icdo": {
            "ner_oncology": [
                "CANCER_DX",
                "HISTOLOGICAL_TYPE",
                "METASTASIS",
                "TUMOR_FINDING",
            ],
            "ner_jsl": ["ONCOLOGICAL"],
        },
        "loinc": {"ner_jsl": ["TEST"], "ner_clinical": ["TEST"]},
        "snomed": {
            "ner_jsl": [
                "PROCEDURE",
                "KIDNEY_DISEASE",
                "CEREBROVASCULAR_DISEASE",
                "HEART_DISEASE",
                "DISEASE_SYNDROME_DISORDER",
                "IMAGINGFINDINGS",
                "SYMPTOM",
                "VS_FINDING",
                "EKG_FINDINGS",
                "COMMUNICABLE_DISEASE",
                "SUBSTANCE",
                "DRUG_INGREDIENT",
                "INTERNAL_ORGAN_OR_COMPONENT",
                "EXTERNAL_BODY_PART_OR_REGION",
                "MODIFIER",
                "TRIGLYCERIDES",
                "ALCOHOL",
                "SMOKING",
                "PREGNANCY",
                "HYPERTENSION",
                "OBESITY",
                "INJURY_OR_POISONING",
                "TEST",
                "HYPERLIPIDEMIA",
                "BMI",
                "ONCOLOGICAL",
                "PSYCHOLOGICAL_CONDITION",
                "LDL",
                "DIABETES",
                "HDL",
            ],
            "ner_snomed_term": ["SNOMED_TERM"],
            "ner_posology": ["DRUG"],
            "ner_clinical": ["PROBLEM", "TREATMENT"],
        },
    }

    # Get the NER models and whitelists for the specified concept
    ner_models = vdb_ner_models[concept]

    # Initialize lists to store pipeline stages and chunk column names
    merger_inputs = []  # Stores names of columns containing NER chunks to be merged
    ner_pipe = []  # Stores the individual stages of the NER pipeline

    # Iterate through the selected NER models and their whitelists
    for ner_model, whitelist in ner_models.items():
        print("Model Name :", ner_model, "---", "White List:", whitelist)

        try:
            # Load a pre-trained MedicalNerModel
            tmp_model = (
                MedicalNerModel.pretrained(ner_model, "en", "clinical/models")
                .setInputCols(["sentence", "token", "word_embeddings"])
                .setOutputCol(ner_model)
                .setLabelCasing("upper")
            )
            ner_pipe.append(tmp_model)  # Add the NER model to the pipeline

            # Add NerConverterInternal to convert NER annotations into chunks
            if len(whitelist) == 0:
                # If no whitelist, use all entities
                ner_pipe.append(
                    NerConverterInternal()
                    .setInputCols(["sentence", "token", ner_model])
                    .setOutputCol(f"{ner_model}_chunk")
                )
            else:
                # If whitelist is provided, filter entities
                ner_pipe.append(
                    NerConverterInternal()
                    .setInputCols(["sentence", "token", ner_model])
                    .setOutputCol(f"{ner_model}_chunk")
                    .setWhiteList(whitelist)
                )

            # Add the chunk column name to the list for merging
            merger_inputs.append(f"{ner_model}_chunk")

        except Exception as e:
            print(e)  # Print any errors during model loading or setup

    # Create a ChunkMergeApproach to combine chunks from different NER models
    chunk_merger = (
        ChunkMergeApproach()
        .setInputCols(merger_inputs)
        .setOutputCol("ner_chunk")
        .setMergeOverlapping(True)
    )
    ner_pipe.append(chunk_merger)  # Add the chunk merger to the pipeline

    # Return the assembled NER pipeline stages
    return ner_pipe


def get_ner_model(concept, spark):
    """
    Creates and returns a Spark NLP pipeline model for Named Entity Recognition (NER).

    Args:
        concept (str): The medical coding system or concept (e.g., "icd10cm", "mesh").

    Returns:
        PipelineModel: A fitted Spark NLP pipeline model for NER.
    """

    # 1. Document Assembler: Converts raw text into Spark NLP Documents
    documentAssembler = DocumentAssembler().setInputCol("text").setOutputCol("document")

    # 2. Sentence Detector: Splits documents into sentences
    sentenceDetector = (
        SentenceDetectorDLModel.pretrained(
            "sentence_detector_dl_healthcare", "en", "clinical/models"
        )
        .setInputCols(["document"])
        .setOutputCol("sentence")
    )

    # 3. Tokenizer: Splits sentences into individual tokens (words)
    tokenizer = Tokenizer().setInputCols("sentence").setOutputCol("token")

    # 4. Word Embeddings: Generates word embeddings for each token
    word_embeddings = (
        WordEmbeddingsModel.pretrained("embeddings_clinical", "en", "clinical/models")
        .setInputCols("sentence", "token")
        .setOutputCol("word_embeddings")
    )

    # 5. Get NER Stages: Dynamically builds NER stages based on the concept
    ner_stages = get_ner_stages(concept, spark)

    # 6. Create Pipeline: Combines all stages into a single pipeline
    pipeline = Pipeline(
        stages=[
            documentAssembler,
            sentenceDetector,
            tokenizer,
            word_embeddings,
            *ner_stages,
        ]
    )

    # 7. Fit Pipeline: Fits the pipeline to an empty DataFrame to initialize it
    empty_df = spark.createDataFrame([[""]]).toDF("text")  # Empty DataFrame for fitting
    print("NER pipeline is ready...")
    model = pipeline.fit(empty_df)

    # 8. Return Model: Returns the fitted NER pipeline model
    return model


def download_vector_db(concept, region_name="us-west-2"):
    import boto3
    from botocore.client import Config

    BUCKET_NAME = "dev.johnsnowlabs.com"
    SOURCE_FILE = f"healthcare_team/resolvers_by_vectordb/{concept}_chroma_db/{concept}_chroma_db.zip"
    target_file = os.path.join(MODEL_LOCATION, f"{concept}_chroma_db.zip")
    extract_path = os.path.join(MODEL_LOCATION, "vector_db")

    config = Config(connect_timeout=3600, read_timeout=70)
    s3 = boto3.client(
        "s3",
        region_name=region_name,
        config=config,
    )
    s3.download_file(BUCKET_NAME, SOURCE_FILE, target_file)
    shutil.unpack_archive(target_file, extract_path)
    os.remove(target_file)


def main(model_ref, language="en", store_license="True", store_model="False"):
    if t_or_f(store_model):
        from sentence_transformers import SentenceTransformer

        ner_model_path = os.path.join(MODEL_LOCATION, "ner_model")
        embeddings_path = os.path.join(MODEL_LOCATION, "embeddings")

        # NER model
        ner_model = get_ner_model(model_ref, spark)
        ner_model.write().overwrite().save(ner_model_path)

        # Embeddings model
        embeddings = SentenceTransformer("BAAI/bge-base-en-v1.5")
        embeddings.save_pretrained(embeddings_path)

        # VectorDB
        download_vector_db(model_ref)

        # Remove model cache directory
        shutil.rmtree("/app/model_cache")

    if not t_or_f(store_license):
        print("Removing the licenses")
        shutil.rmtree("/root/.johnsnowlabs/licenses")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Install johnsnowlabs and requested models"
    )
    parser.add_argument(
        "--model",
        required=True,
        type=str,
        help="Name of the model",
    )
    parser.add_argument(
        "--language",
        required=False,
        type=str,
        default="en",
        help="The language identifier",
    )
    parser.add_argument(
        "--store_license",
        required=False,
        default="True",
        type=str,
        help="Store the license",
    )

    parser.add_argument(
        "--store_model",
        required=False,
        default="False",
        type=str,
        help="Store the model",
    )

    args = parser.parse_args()
    main(
        model_ref=args.model,
        language=args.language,
        store_license=args.store_license,
        store_model=args.store_model,
    )
