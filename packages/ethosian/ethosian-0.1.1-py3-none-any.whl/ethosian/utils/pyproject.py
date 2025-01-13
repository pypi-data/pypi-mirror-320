from pathlib import Path
from typing import Optional, Dict

from ethosian.utils.log import logger


def read_pyproject_ethosian(pyproject_file: Path) -> Optional[Dict]:
    logger.debug(f"Reading {pyproject_file}")
    try:
        import tomli

        pyproject_dict = tomli.loads(pyproject_file.read_text())
        ethosian_conf = pyproject_dict.get("tool", {}).get("ethosian", None)
        if ethosian_conf is not None and isinstance(ethosian_conf, dict):
            return ethosian_conf
    except Exception as e:
        logger.error(f"Could not read {pyproject_file}: {e}")
    return None
