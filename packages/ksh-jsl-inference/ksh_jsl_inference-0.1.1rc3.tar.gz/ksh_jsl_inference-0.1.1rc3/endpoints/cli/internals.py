from endpoints.johnsnowlabs.inference.model import BaseInferenceModel
from endpoints.container import utils
import click
import uuid
from endpoints.container.internals import BuildDockerImageRequest
from endpoints.log_utils import logger
from typing import Union
import os
import importlib

from endpoints.utils import Platform, Recipe


def _get_default_output_dir(platform: Platform) -> str:
    """
    Generates the default output directory under the user's home folder
    for the given platform.
    """
    home_dir = os.path.expanduser("~")
    return os.path.join(home_dir, ".jsl_inference", platform.value, str(uuid.uuid4()))


def _generate_docker_files(model: str, **kwargs) -> str:
    """Cli helper to generate Docker files for a given model."""
    try:
        kwargs["output_dir"] = kwargs.get("output_dir") or _get_default_output_dir(
            Platform(kwargs.get("platform"))
        )

        inference_model = kwargs.get("inference_model")
        legacy = kwargs.get("legacy", False)

        logger.info(f"Generating Docker files for model: {model}")
        inference_model_obj = None
        kwargs["recipe"] = Recipe(kwargs["recipe"])
        if inference_model:
            inference_model_obj = _get_inference_model_from_path(
                inference_model, legacy=legacy
            )
            kwargs["inference_model"] = inference_model_obj
        output_dir = utils.generate_docker_files(model, **kwargs)
        logger.info(f"Docker files generated in: {output_dir}")
        return output_dir
    except Exception as e:
        logger.exception(f"An error occurred: {str(e)}")
        raise click.ClickException("Failed to generate Docker files.")


def _load_inference_model(inference_model: str) -> BaseInferenceModel:
    logger.debug(f"Loading inference model: {inference_model}")
    module_name, class_name = inference_model.rsplit(".", 1)
    module = importlib.import_module(module_name)
    inference_class = getattr(module, class_name)
    return inference_class()


def _get_inference_model_from_path(
    inference_model: str, legacy: bool = False
) -> Union[BaseInferenceModel, str]:
    """
    Load the inference model.
    If legacy=True, the inference logic is loaded from the specified path.
    """
    if legacy:
        if os.path.isfile(inference_model):
            return inference_model
        raise ValueError("Inference model path is required.")
    else:
        if not inference_model:
            raise ValueError("Inference model is required.")
        return _load_inference_model(inference_model)


def build_docker_image(model: str, **kwargs):
    """Cli helper to build a Docker image for a given model."""

    docker_files_location = _generate_docker_files(model, **kwargs)
    req = BuildDockerImageRequest(model=model, **kwargs)

    try:
        image_name = req.image_name or req.model
        utils.build_docker_image(
            image_name=image_name,
            license_path=req.license_path,
            build_context_dir=docker_files_location,
            no_cache=req.no_cache,
        )
    except Exception as e:
        logger.exception(f"An error occurred while building the Docker image: {str(e)}")
        raise click.ClickException("Failed to build Docker image.")


def run_local(
    model: str,
    inference_model: str,
    recipe: Recipe,
    platform: Platform,
    language: str,
    port=8080,
):
    """Helper to run the model locally."""
    from endpoints.container.serve import setup_env_and_start_server
    from endpoints.cli.internals import _load_inference_model

    inference_model_obj = None
    if inference_model:
        inference_model_obj = _load_inference_model(inference_model)

    setup_env_and_start_server(
        platform=platform,
        model=model,
        language=language,
        inference_model=inference_model_obj,
        recipe=recipe,
        port=port,
    )
