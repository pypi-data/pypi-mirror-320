import click
from typing import Optional

from endpoints.cli import internals
from endpoints.cli.options import common_options

from endpoints.cli import cli

from endpoints.utils import Platform, Recipe


@cli.group()
def sagemaker():
    """
    Group of commands related to SageMaker functionality.
    """
    pass


@sagemaker.command()
@common_options
@click.option(
    "--output-dir",
    help="Output directory for the Docker files. If not provided, a default directory will be used.",
)
def generate_docker_files(model: str, **kwargs):
    """
    Generates Docker files for the specified model in a SageMaker-compatible format.

    Parameters:
        model (str): The model to generate Docker files for.
        johnsnowlabs_version (str): Version of the John Snow Labs library to include.
        store_license (bool): Flag indicating if the license should be included in the Docker image.
        store_model (bool): Flag indicating if the model should be included in the Docker image.
        language (str): Language of the model (default: 'en').
        legacy (bool): Flag indicating if legacy process of generating Docker files should be used.
        inference_model (str): Import path of a class (Should be a subclass of BaseInferenceModel) For Legacy mode, this should be a path to an endpoint_logic.py file.
        recipe (str): Recipe to use for generating Docker files (default: 'healthcare_nlp').
        output_dir (str): Directory to store the generated Docker files. Defaults to a unique directory if not provided.

    Raises:
        click.ClickException: If an error occurs during Docker file generation.
    """

    output_dir = internals._generate_docker_files(
        model=model, platform=Platform.SAGEMAKER, **kwargs
    )


@sagemaker.command()
@common_options
@click.option(
    "--image-name",
    default=None,
    help="Name of the Docker image to build. Defaults to the model name if not provided.",
)
@click.option(
    "--license-path",
    required=False,
    help="Path to the license file required to build the Docker image.By default, uses licenses set in the JSL_HOME.",
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
        store_model (bool): Flag indicating if the model should be included in the Docker image.
        language (str): Language of the model (default: 'en').
        license_path (str): Path to the license file required for the Docker image.
        image_name (str): Name of the Docker image to build. Defaults to the model name if not provided.
        inference_model (str): Import path of a class (Should be a subclass of BaseInferenceModel) For Legacy mode, this should be a path to an endpoint_logic.py file.
        legacy (bool): Flag indicating if legacy process of generating Docker files should be used.
        recipe (str): Recipe to use for generating Docker files (default: 'healthcare_nlp').
        no_cache (bool): Flag to disable Docker cache during the build process.

    Raises:
        click.ClickException: If the Docker image build fails.
    """
    internals.build_docker_image(model, platform=Platform.SAGEMAKER, **kwargs)


@sagemaker.command()
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
    """Run a local instance of the Sagemaker Inference container."""
    internals.run_local(
        model=model,
        language=language,
        platform=Platform.SAGEMAKER,
        inference_model=inference_model,
        recipe=Recipe(recipe),
        port=port,
    )
