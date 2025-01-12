import os
import click
from typing import Optional
import subprocess

from endpoints.cli.options import common_options
from endpoints.cli import cli, internals
from endpoints.log_utils import logger
from endpoints.utils import Platform, Recipe


@cli.group()
def snowflake():
    """
    Group of commands related to Snowflake functionality.
    """
    pass


@snowflake.command()
@common_options
@click.option(
    "--output-dir",
    help="Output directory for the Docker files. If not provided, a default directory will be used.",
)
def generate_docker_files(model: str, **kwargs):
    """
    Generates Docker files for the specified model for Snowflake.
    """

    output_dir = internals._generate_docker_files(
        model=model,
        platform=Platform.SNOWFLAKE,
        **kwargs,
    )


@snowflake.command()
@common_options
@click.option(
    "--image-name",
    default=None,
    help="Name of the Docker image to build. Defaults to the model name if not provided.",
)
@click.option(
    "--license-path",
    required=False,
    help="Path to the license file required to build the Docker image.",
)
@click.option(
    "--no-cache",
    is_flag=True,
    default=False,
    help="Disable Docker cache during build.",
)
def build_docker_image(model: str, **kwargs):
    """
    Builds a Docker image for the specified model.

    Parameters:
        model (str): The model for which the Docker image is being built.
        johnsnowlabs_version (str): Version of the John Snow Labs library to include.
        store_license (bool): Flag indicating if the license should be included in the Docker image.
        store_model (bool): Flag indicating if the model should be included in the Docker image. It is set True for snowflake and cannot be changed.
        language (str): Language of the model (default: 'en').
        license_path (str): Path to the license file required for the Docker image.
        inference_model (str): Import path of a class (Should be a subclass of BaseInferenceModel) For Legacy mode, this should be a path to an endpoint_logic.py file.
        legacy (bool): Flag indicating if legacy process of generating Docker files should be used.

    Raises:
        click.ClickException: If the Docker image build fails.
    """
    internals.build_docker_image(model=model, platform=Platform.SNOWFLAKE, **kwargs)


@snowflake.command()
@click.option("--model", required=False, help="The model to run locally.")
@click.option(
    "--language",
    required=False,
    default="en",
    help="Language of the model to load (default: 'en')",
)
@click.option(
    "--inference_model",
    required=False,
    help="Inference model to use. Must be a subclass of BaseInference",
)
@click.option(
    "--recipe",
    required=False,
    type=click.Choice([recipe.value for recipe in Recipe], case_sensitive=False),
    default=Recipe.HEALTHCARE_NLP.value,
    help="Recipe to use. Valid values: "
    + ", ".join([recipe.value for recipe in Recipe]),
)
@click.option("--port", required=False, default=8080)
def run_local(model: str, language: str, inference_model: str, recipe: str, port: int):
    """Run a local instance of the Snowflake Inference container"""
    internals.run_local(
        model=model,
        language=language,
        inference_model=inference_model,
        platform=Platform.SNOWFLAKE,
        recipe=Recipe(recipe),
        port=port,
    )
