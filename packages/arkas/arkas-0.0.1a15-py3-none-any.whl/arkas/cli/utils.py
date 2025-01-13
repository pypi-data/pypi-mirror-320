r"""Contain some utility functions for command lines."""

from __future__ import annotations

__all__ = ["get_original_cwd", "log_run_info"]

import logging
from pathlib import Path
from unittest.mock import Mock

from coola.utils.path import sanitize_path

import arkas
from arkas.utils.imports import (
    check_omegaconf,
    is_hydra_available,
    is_omegaconf_available,
)

if is_hydra_available():  # pragma: no cover
    import hydra
    from hydra.core.hydra_config import HydraConfig

if is_omegaconf_available():
    from omegaconf import DictConfig, OmegaConf
else:  # pragma: no cover
    DictConfig = Mock()

logger = logging.getLogger(__name__)

# ASCII logo generated from https://ascii.co.uk/art/bear and
# https://patorjk.com/software/taag/#p=testall&f=Graffiti&t=arkas%0A
LOGO = rf"""
           .--.              .--.
          : (\ ". _......_ ." /) :
           '.    `        `    .'                    __
            /'   _        _   `\       _____ _______|  | _______    ______
           /     0}}      {{0     \      \__  \\_  __ \  |/ /\__  \  /  ___/
          |       /      \       |      / __ \|  | \/    <  / __ \_\___ \
          |     /'        `\     |     (____  /__|  |__|_ \(____  /____  >
           \   | .  .==.  . |   /           \/           \/     \/     \/
            '._ \.' \__/ './ _.'
            /  ``'._-''-_.'``  \
                    `--`

version: {arkas.__version__}"""


def get_original_cwd() -> Path:
    r"""Get the original working directory the experiment was launched
    from.

    The problem is that Hydra change the working directory when the
    application is launched.

    Returns:
        If Hydra is initialized, it returns the original working
            directory otherwise it returns the current working
            directory.

    Example usage:

    ```pycon

    >>> from arkas.cli.utils import get_original_cwd
    >>> get_original_cwd()

    ```
    """
    if is_hydra_available() and HydraConfig.initialized():
        return sanitize_path(hydra.utils.get_original_cwd())
    return Path.cwd()


def log_run_info(config: DictConfig) -> None:
    """Log some information about the current run.

    Args:
        config: The config of the run.

    Example usage:

    ```pycon

    >>> from omegaconf import OmegaConf
    >>> from arkas.cli.utils import log_run_info
    >>> log_run_info(OmegaConf.create())

    ```
    """
    check_omegaconf()
    logger.info(LOGO)
    logger.info("Original working directory: %s", get_original_cwd())
    logger.info("Current working directory: %s", Path.cwd())
    logger.info("Config:\n%s", OmegaConf.to_yaml(config))
