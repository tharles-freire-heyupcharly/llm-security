import sys
from pathlib import Path

# Garante que `labcore` e `backend` sejam importáveis independente do cwd.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest


@pytest.fixture()
def client():
    """TestClient com estado (defesas/logs/contadores) resetado a cada teste."""
    from fastapi.testclient import TestClient
    from backend.main import app
    from labcore import logging_util
    from labcore.scenarios import api_exposta

    logging_util.clear()
    api_exposta.reset()
    with TestClient(app) as c:
        c.post("/api/defenses", json={
            "input_validation": False, "output_validation": False,
            "least_privilege": False, "api_security": False,
        })
        yield c
    logging_util.clear()
    api_exposta.reset()
