import os


MODEL_LOCATION = "/opt/ml/model"
__version__ = "0.1.1rc5"

JSL_DOWNLOAD_PACKAGES = os.environ.get("JSL_DOWNLOAD_PACKAGES", True)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PACKAGE_NAME = "ksh-jsl-inference"
