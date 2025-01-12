import os
import base64
from johnsnowlabs.nlp import settings
import json
import time


def is_license_valid(license_file):
    """Check if the license file is valid"""
    if not os.path.isfile(license_file):
        raise FileNotFoundError(f"Provided license file does not exist: {license_file}")

    with open(license_file, "r") as f:
        content = f.read()
        license_content = json.loads(content)
        license = license_content.get("HC_LICENSE") or license_content.get(
            "OCR_LICENSE"
        )

        token_payload = license.split(".")[1]
        token_payload_decoded = str(base64.b64decode(token_payload + "=="), "utf-8")
        payload = json.loads(token_payload_decoded)
        # Make sure license is active
        is_active = time.time() < payload.get("exp")
        # Make sure license has atleast healthcare scopes
        has_inference_scope = "healthcare:inference" in payload.get("scope")
        return is_active and has_inference_scope


def find_license_from_jsl_home():
    source_path = settings.license_dir
    """ List all json files in the license directory """
    license_files = [
        os.path.join(source_path, f)
        for f in os.listdir(source_path)
        if (f.endswith(".json") and not f.startswith("info.json"))
    ]

    try:
        return next(file for file in license_files if is_license_valid(file))
    except Exception:
        raise Exception("Active JSL License Required")
