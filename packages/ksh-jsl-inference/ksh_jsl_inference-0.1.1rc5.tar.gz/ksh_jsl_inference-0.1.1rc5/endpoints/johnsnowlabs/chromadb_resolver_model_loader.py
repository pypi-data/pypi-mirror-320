import multiprocessing
import sys
import torch
from sparknlp.pretrained import LightPipeline, PretrainedPipeline
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from endpoints.log_utils import logger
from endpoints.johnsnowlabs.spark_session import spark


import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

__import__("pysqlite3")
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")


spark = spark


class ModelLoader:
    _model = None
    _local_db = None
    _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    @classmethod
    def load_model(cls):
        if cls._model is None:
            try:
                logger.info("Loading JSL NER model from /opt/ml/model/ner_model")
                cls._model = PretrainedPipeline.from_disk("/opt/ml/model/ner_model")
                logger.info("Model loaded successfully")
            except Exception as e:
                logger.error(f"Error loading model: {e}")
                raise
        return cls._model, LightPipeline(cls._model.model)

    @classmethod
    def load_local_db(cls):
        if cls._local_db is None:
            try:
                logger.info("Loading local DB from /opt/ml/model/vector_db")
                embeddings = HuggingFaceEmbeddings(
                    model_name="/opt/ml/model/embeddings",
                    model_kwargs={"device": cls._device},
                )
                cls._local_db = Chroma(
                    persist_directory="/opt/ml/model/vector_db",
                    embedding_function=embeddings,
                )
                logger.info("Local DB loaded successfully")
            except Exception as e:
                logger.error(f"Error loading model: {e}")
                raise
        return cls._local_db


logger.debug(f"vCPU Count: {multiprocessing.cpu_count()}")
pretrained_pipeline, light_pipeline = ModelLoader.load_model()
local_db = ModelLoader.load_local_db()
