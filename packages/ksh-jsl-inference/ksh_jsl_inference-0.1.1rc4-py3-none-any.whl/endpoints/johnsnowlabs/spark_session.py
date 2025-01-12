import os
from endpoints.log_utils import logger
import sys
from johnsnowlabs import nlp


os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable


def start_spark():
    logger.info("Starting spark session")

    spark = nlp.start()
    spark.sparkContext.setLogLevel("ERROR")

    logger.info("Spark session started")
    return spark


spark = start_spark()
