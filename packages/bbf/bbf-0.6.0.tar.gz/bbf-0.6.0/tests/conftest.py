"""Defines pytest fixtures"""

import pytest
import lemaitre.bandpasses


@pytest.fixture(scope="session")
def filterlib():
    return lemaitre.bandpasses.get_filterlib(rebuild=True)
