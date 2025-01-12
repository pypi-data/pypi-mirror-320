from endpoints.utils import Platform
from endpoints.johnsnowlabs.inference.model import BaseInferenceModel
from .serve import serve_container
import os


# Default entrypoint for the Docker containers
def _init(command, inference_model: BaseInferenceModel):
    # For Sagemaker, serve and train are the possible commands
    platform = Platform(os.environ.get("PLATFORM"))
    if command == "serve":
        serve_container(platform=platform, inference_model=inference_model)
    else:
        raise NotImplemented("Command not implemented")
