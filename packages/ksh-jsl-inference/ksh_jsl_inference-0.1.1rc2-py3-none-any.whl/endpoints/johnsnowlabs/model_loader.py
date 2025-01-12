import multiprocessing

from sparknlp.pretrained import LightPipeline, PretrainedPipeline
from endpoints.log_utils import logger
from endpoints.johnsnowlabs.spark_session import spark

spark = spark


class ModelLoader:
    _model = None

    @classmethod
    def load_model(cls):
        if cls._model is None:
            try:
                logger.info("Loading model from /opt/ml/model")
                cls._model = PretrainedPipeline.from_disk("/opt/ml/model")
                logger.info("Model loaded successfully")
            except Exception as e:
                logger.error(
                    f"Error loading model: {e}. Please make sure you have downloaded the model and placed it on /opt/ml/model"
                )
                raise
        return LightPipeline(cls._model.model)


logger.debug(f"vCPU Count: {multiprocessing.cpu_count()}")
light_pipeline = ModelLoader.load_model()
