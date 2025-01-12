import inspect
import os
import shutil
from typing import List
from typing import Optional
import subprocess
from endpoints.container.internals import GenerateDockerFilesRequest
from endpoints.johnsnowlabs.license_utils import (
    find_license_from_jsl_home,
    is_license_valid,
)
from endpoints.settings import PACKAGE_NAME, __version__


from endpoints.johnsnowlabs.inference.model import BaseInferenceModel
from endpoints.johnsnowlabs.inference.chroma_resolver_model import (
    ChromaDbResolverInferenceModel,
)
from endpoints.johnsnowlabs.inference.medical_nlp_model import MedicalNlpInferenceModel
from endpoints.log_utils import logger
from endpoints.utils import (
    Platform,
    Recipe,
    copy_and_replace,
    generate_license_file,
)


current_dir = os.path.dirname(__file__)


def get_requirements(
    platform: Platform,
    johnsnowlabs_version: Optional[str] = None,
    inference: Optional[BaseInferenceModel] = None,
) -> List[str]:
    """
    Generates a list of requirements  for the specified platform and inference model.

    Args:
        johnsnowlabs_version (str): The version of the John Snow Labs library.
        platform (Platform): The platform for which the requirements are being generated.
        inference (BaseInferenceModel): The inference model to include in the requirements.

    Returns:
        list: A list of requirements.
    """
    requirements = []
    if johnsnowlabs_version:
        requirements = [f"johnsnowlabs=={johnsnowlabs_version}"]

    additional_packages = platform.get_python_requirements()
    if inference:
        additional_packages.extend(inference.get_python_requirements())
    additional_packages = [
        package
        for package in additional_packages
        if not package.startswith("johnsnowlabs")
    ]
    ##TODO: Add checks for requirements conflicts
    requirements.extend(additional_packages)

    return requirements


def _get_requirements_for_docker_image(req: GenerateDockerFilesRequest):
    """Helper function that generates requirements based on the platform and inference model."""

    requirements = []
    if req.legacy:
        requirements = [
            "uvicorn",
            "fastapi",
        ]
        if req.recipe == Recipe.CHROMADB_RESOLVER:
            requirements.extend(
                ChromaDbResolverInferenceModel().get_python_requirements()
            )
    else:
        requirements = [f"{PACKAGE_NAME}=={__version__}"]

    inference_obj = None
    if isinstance(req.inference_model, BaseInferenceModel):
        inference_obj = req.inference_model
    requirements.extend(
        get_requirements(req.platform, req.johnsnowlabs_version, inference_obj)
    )

    return requirements


def __copy_templates(templates_dir: str, output_dir: str):
    shutil.copytree(templates_dir, output_dir, dirs_exist_ok=True)
    shutil.rmtree(f"{output_dir}/__pycache__", ignore_errors=True)


def __use_legacy_chroma_db_resolver_templates(output_dir: str):
    chromadb_template_dir = f"{current_dir}/chromadb_resolver_templates"
    specific_files = ["endpoint_logic.py", "model_loader.py", "installer.py"]
    for file in specific_files:
        source = os.path.join(chromadb_template_dir, file)
        if os.path.exists(source):
            shutil.copy2(source, output_dir)


def __include_routes(req: GenerateDockerFilesRequest):
    expected_files = ["__init__.py", "healthcheck.py", f"{req.platform.value}.py"]
    all_files = [file for file in os.listdir(os.path.join(req.output_dir, "routers"))]
    for file in all_files:
        if file not in expected_files:
            os.remove(os.path.join(req.output_dir, "routers", file))

    with open(f"{req.output_dir}/app.py", "a+") as f:
        f.write(f"from routers import {req.platform.value}\n")
        f.write(f"app.include_router({req.platform.value}.router)\n")


def _generate_legacy_docker_files(req: GenerateDockerFilesRequest):

    template_base_dir = f"{current_dir}/templates"

    __generate_requirements_file(req)
    __copy_templates(template_base_dir, req.output_dir)
    generate_license_file(req.output_dir)

    if req.recipe == Recipe.CHROMADB_RESOLVER:
        __use_legacy_chroma_db_resolver_templates(req.output_dir)
    __include_routes(req)
    # Replace placeholders in Dockerfile
    copy_and_replace(
        f"{req.output_dir}/Dockerfile",
        f"{req.output_dir}/Dockerfile",
        {
            "{{JOHNSNOWLABS_VERSION}}": req.johnsnowlabs_version,
            "{{STORE_LICENSE}}": str(req.store_license),
            "{{STORE_MODEL}}": str(req.store_model),
            "{{MODEL_TO_LOAD}}": req.model,
            "{{LANGUAGE}}": req.language,
        },
    )
    if isinstance(req.inference_model, str):
        shutil.copy(req.inference_model, f"{req.output_dir}/endpoint_logic.py")


def __generate_requirements_file(req):
    requirements = _get_requirements_for_docker_image(req)

    logger.debug(f"Generating requirements file in: {req.output_dir}")
    with open(f"{req.output_dir}/requirements.txt", "w+") as f:
        f.write("\n".join(requirements))


def _get_env_setup_command(req: GenerateDockerFilesRequest):

    inference_class_name = req.inference_model.__class__.__name__
    setup_container_args = {
        "platform": f"Platform.{req.platform.name}",
        "inference_model": f"{inference_class_name}()",
        "language": f"'{req.language}'",
        "johnsnowlabs_version": f"'{req.johnsnowlabs_version}'",
        "store_license": req.store_license,
    }
    if req.store_model:
        setup_container_args["model"] = f"'{req.model}'"
    args_string = ",".join(
        [f"{key}={value}" for key, value in setup_container_args.items()]
    )
    container_serve_command = f"S({args_string})"
    setup_env_command = (
        "python3 -c "
        f'"from inference_model import {inference_class_name};'
        "from endpoints.utils import Platform;"
        "from endpoints.container.serve import setup_container_env as S;"
        f'{container_serve_command}"'
    )
    return setup_env_command


def __get_entrypoint_command(inference: BaseInferenceModel):
    inference_class_name = inference.__class__.__name__
    return (
        "import sys;"
        f"from inference_model import {inference_class_name};"
        f"from endpoints import container as C;"
        f"C._init(sys.argv[1], inference_model={inference_class_name}())"
    )


def _generate_docker_files_v1(req: GenerateDockerFilesRequest):
    __generate_requirements_file(req)

    generate_license_file(req.output_dir)
    setup_env_command = _get_env_setup_command(req)

    entrypoint_command = __get_entrypoint_command(req.inference_model)

    copy_and_replace(
        f"{current_dir}/Dockerfile",
        f"{req.output_dir}/Dockerfile",
        {
            "{{STORE_LICENSE}}": str(req.store_license),
            "{{STORE_MODEL}}": str(req.store_model),
            "{{MODEL_TO_LOAD}}": req.model,
            "{{LANGUAGE}}": req.language,
            "{{ENTRYPOINT}}": f'ENTRYPOINT ["python3", "-c", "{entrypoint_command}"]',
            "{{ENVIRONMENT_VARIABLES}}": f"ENV PLATFORM={req.platform.value}",
            "{{SETUP_ENVIRONMENT}}": setup_env_command,
        },
    )
    file = inspect.getfile(req.inference_model.__class__)
    shutil.copy(file, f"{req.output_dir}/inference_model.py")


def _generate_docker_files(req: GenerateDockerFilesRequest):
    """Common logic for generating Docker files across different recipes."""

    os.makedirs(req.output_dir, exist_ok=True)
    if req.legacy:
        _generate_legacy_docker_files(req)
    else:
        if not isinstance(req.inference_model, BaseInferenceModel):
            raise ValueError(
                "Inference model must be an instance of BaseInferenceModel"
            )
        _generate_docker_files_v1(req)

    return req.output_dir


def generate_docker_files(model: str, **kwargs) -> str:
    """Main function to generate Docker files based on recipe type."""

    req = GenerateDockerFilesRequest(model=model, **kwargs)

    inference_obj = req.inference_model

    if not req.legacy:
        inference_obj = req.inference_model or req.recipe.get_default_inference_model()
        req.inference_model = inference_obj
        if isinstance(inference_obj, str):
            raise ValueError(
                "Inference model must be an instance of BaseInferenceModel"
            )

        if req.recipe == Recipe.HEALTHCARE_NLP:
            if not issubclass(inference_obj.__class__, MedicalNlpInferenceModel):
                raise ValueError("Inference class must inherit from MedicalNlpModel")

        elif req.recipe == Recipe.CHROMADB_RESOLVER:
            if not issubclass(inference_obj.__class__, ChromaDbResolverInferenceModel):
                raise ValueError(
                    "Inference class must inherit from ChromaDbResolverModel"
                )

        else:
            raise NotImplementedError(f"Recipe '{req.recipe}' is not implemented.")

    return _generate_docker_files(req)


def build_docker_image(
    image_name: str,
    license_path: Optional[str],
    build_context_dir: str,
    no_cache: bool = False,
    image_tag: str = "latest",
):
    """Builds a Docker image using the specified build context directory"""
    if license_path and is_license_valid(license_path):
        license_to_use = license_path
    else:
        license_to_use = find_license_from_jsl_home()

    build_command = [
        "docker",
        "build",
    ]

    if no_cache:
        build_command.append("--no-cache")

    build_command.extend(
        [
            "--secret",
            f"id=license,src={license_to_use}",
            "-t",
            f"{image_name}:{image_tag}",
            build_context_dir,
        ]
    )

    logger.info(f"Executing Docker build command: {' '.join(build_command)}")

    subprocess.run(build_command, check=True)
    logger.info(f"Docker image '{image_name}:latest' built successfully!")


def is_valid_output_dir(directory: str) -> bool:
    """
    Validates if the specified directory contains the required Docker files.

    Args:
        directory (str): Path to the directory to validate.

    Returns:
        bool: True if the directory contains the required files, False otherwise.
    """
    if not directory or not os.path.isdir(directory):
        return False

    required_files = ["Dockerfile", "requirements.txt"]
    return all(os.path.isfile(os.path.join(directory, file)) for file in required_files)


def install_johnsnowlabs_from_docker_secret():
    from johnsnowlabs import nlp

    nlp.install(
        json_license_path="/run/secrets/license",
        browser_login=False,
        force_browser=False,
    )
