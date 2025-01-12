import uvicorn
import shutil
from endpoints.container.utils import (
    get_requirements,
    install_johnsnowlabs_from_docker_secret,
)
from endpoints.log_utils import logger
import os
from fastapi import FastAPI
from typing import Optional
import logging
from endpoints.settings import JSL_DOWNLOAD_PACKAGES

from endpoints.johnsnowlabs.inference.model import BaseInferenceModel
from endpoints.johnsnowlabs.inference.medical_nlp_model import MedicalNlpInferenceModel
from endpoints.model import download_model
from endpoints.pip_utils import install
from endpoints.utils import Platform, Recipe
from .routers import healthcheck


def _configure_logging():
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(level=log_level)


def _create_fast_api_app(
    inferenceModel: Optional[BaseInferenceModel] = MedicalNlpInferenceModel(),
    include_sagemaker_route=False,
    include_snowflake_route=False,
):
    app = FastAPI()
    _configure_logging()
    app.state.inference_model = inferenceModel

    app.include_router(healthcheck.router)
    if include_sagemaker_route:
        from .routers import sagemaker

        app.include_router(sagemaker.router)
    if include_snowflake_route:
        from .routers import snowflake

        app.include_router(snowflake.router)
    return app


def serve_container(
    platform: Platform,
    port=8080,
    inference_model: BaseInferenceModel = MedicalNlpInferenceModel(),
):
    # Make an initial request so that all dependencies all loaded before the server starts
    # This makes the first request faster
    inference_model.predict({inference_model._input._field: "Sample request"})

    app = _create_fast_api_app(
        inference_model,
        include_sagemaker_route=(platform == Platform.SAGEMAKER),
        include_snowflake_route=(platform == Platform.SNOWFLAKE),
    )

    uvicorn.run(app, host="0.0.0.0", port=port)


def _setup_env(
    platform: Platform,
    inference_model: BaseInferenceModel,
    model: Optional[str],
    language: str = "en",
    recipe: Recipe = Recipe.HEALTHCARE_NLP,
    johnsnowlabs_version: Optional[str] = None,
):
    install_python_requirements(platform, inference_model, johnsnowlabs_version)
    if model:
        download_model(
            model=model,
            language=language,
            recipe=recipe,
        )


def _cleanup_container():
    home_dir = os.path.expanduser("~")
    paths_to_remove = [
        os.path.join(home_dir, "cache_pretrained"),
        os.path.join(home_dir, ".javacpp"),
        os.path.join("/tmp"),
    ]
    for path in paths_to_remove:
        shutil.rmtree(path, ignore_errors=True)


def setup_container_env(
    platform: Platform,
    inference_model: BaseInferenceModel,
    language: str = "en",
    johnsnowlabs_version: Optional[str] = None,
    model: Optional[str] = None,
    store_license: bool = True,
):
    _configure_logging()
    install_johnsnowlabs_from_docker_secret()
    _setup_env(
        platform=platform,
        inference_model=inference_model,
        model=model,
        language=language,
        johnsnowlabs_version=johnsnowlabs_version,
    )
    if not store_license:
        logger.info("Removing the licenses")
        shutil.rmtree(
            f"/{os.path.expanduser('~')}/.johnsnowlabs/licenses", ignore_errors=True
        )

    _cleanup_container()


def setup_env_and_start_server(
    platform: Platform,
    model: Optional[str] = None,
    recipe: Recipe = Recipe.HEALTHCARE_NLP,
    inference_model: Optional[BaseInferenceModel] = MedicalNlpInferenceModel(),
    language: str = "en",
    port: int = 8080,
):
    inference_model_obj = inference_model or recipe.get_default_inference_model()
    _setup_env(
        model=model,
        recipe=recipe,
        inference_model=inference_model_obj,
        language=language,
        platform=platform,
    )
    serve_container(
        platform=platform,
        port=port,
        inference_model=inference_model_obj,
    )


def install_python_requirements(
    platform: Platform,
    inference_model: BaseInferenceModel,
    johnsnowlabs_version: Optional[str] = None,
):
    if not JSL_DOWNLOAD_PACKAGES:
        logger.info("Skipping installation of python requirements")
    else:
        requirements = get_requirements(
            platform=platform,
            inference=inference_model,
            johnsnowlabs_version=johnsnowlabs_version,
        )
        install(requirements)
