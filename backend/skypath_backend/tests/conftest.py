#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pytest fixtures for SkyPath backend tests.
Responsibility: SkyPath Flight Connection Search.
"""
import pytest
from fastapi.testclient import TestClient

from skypath_backend.app import app


@pytest.fixture(scope="module")
def client():
    """Create TestClient with app; startup runs and loads flights from flights.json."""
    with TestClient(app) as c:
        yield c
