import sys
from typing import List
from endpoints.log_utils import logger
import subprocess


def install(packages: List[str]):
    """Install multiple packages using pip"""
    logger.info(f"Installing packages: {' '.join(packages)}")
    if packages:
        subprocess.check_call([sys.executable, "-m", "pip", "install", *packages])
