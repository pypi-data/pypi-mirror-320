r"""Define some utility functions for testing."""

from __future__ import annotations

__all__ = [
    "colorlog_available",
    "hya_available",
    "hydra_available",
    "markdown_available",
    "matplotlib_available",
    "omegaconf_available",
    "plotly_available",
    "scipy_available",
]

import pytest

from arkas.utils.imports import (
    is_colorlog_available,
    is_hya_available,
    is_hydra_available,
    is_markdown_available,
    is_matplotlib_available,
    is_omegaconf_available,
    is_plotly_available,
    is_scipy_available,
)

colorlog_available = pytest.mark.skipif(not is_colorlog_available(), reason="requires colorlog")
hya_available = pytest.mark.skipif(not is_hya_available(), reason="requires hya")
hydra_available = pytest.mark.skipif(not is_hydra_available(), reason="requires hydra")
markdown_available = pytest.mark.skipif(not is_markdown_available(), reason="requires markdown")
matplotlib_available = pytest.mark.skipif(
    not is_matplotlib_available(), reason="requires matplotlib"
)
omegaconf_available = pytest.mark.skipif(not is_omegaconf_available(), reason="requires omegaconf")
plotly_available = pytest.mark.skipif(not is_plotly_available(), reason="requires plotly")
scipy_available = pytest.mark.skipif(not is_scipy_available(), reason="requires scipy")
