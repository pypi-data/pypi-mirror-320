#!/usr/bin/env python3
""" Convert Python code modules to JSON and CSV for publication.

When adding new modules:

- Import module
- Add new module to for loop in __main__
"""
import sys
import json
from pathlib import Path

from fhir.resources.codesystem import CodeSystem
from pydantic import ValidationError

from terminology.resources.code_systems import extraoral_2d_photographic_vews, extraoral_3d_visible_light_views, intraoral_3d_visible_light_views, intraoral_2d_photographic_views

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# Create formatter and add it to the handler
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(ch)


build_path = Path('.', 'docs')


def save_code_system_to_fhir(module, filename: Path):
    logger.info(f"Processing {module.__name__}")

    code_systems = {name: getattr(module, name) for name in dir(module)
                    if isinstance(getattr(module, name), type) and issubclass(getattr(module, name), CodeSystem)}

    if not code_systems:
        logger.warning(
            f"No CodeSystem instances found in the module {module.__name__}")
        return

    for name, code_system_class in code_systems.items():
        try:
            code_system_instance = code_system_class()
        except ValidationError as e:
            logger.debug(
                f"CodeSystem {code_system_class.__name__} is not valid")
            continue
        filename = filename / code_system_instance.url.split('/')[-1]
        filename.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"Saving {code_system_class.__name__} to {filename}")
        with open(filename, 'w') as f:
            json.dump(code_system_instance.model_dump(), f, indent=4)


def main():
    for codes_system in (
            extraoral_2d_photographic_vews,
            extraoral_3d_visible_light_views,
            intraoral_3d_visible_light_views,
            intraoral_2d_photographic_views
    ):
        save_code_system_to_fhir(
            codes_system, build_path / 'fhir')


if __name__ == "__main__":
    sys.exit(main())
