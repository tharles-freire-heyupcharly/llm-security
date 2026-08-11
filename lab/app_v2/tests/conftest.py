import sys
from pathlib import Path

# Garante que `labcore` e `backend` sejam importáveis independente do cwd.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

CASSETTE_DIR = Path(__file__).resolve().parent / "cassettes"


@pytest.fixture()
def client():
    """TestClient com estado (defesas/logs/contadores/modo de IA/tenant) resetado a cada teste."""
    from fastapi.testclient import TestClient
    from backend.main import app
    from labcore import config, logging_util, store
    from labcore.scenarios import api_exposta

    logging_util.clear()
    api_exposta.reset()
    store.reset()
    config.LLM_MODE = "mock"
    config.TENANT_ID = "financeira-A"
    with TestClient(app) as c:
        c.post("/api/defenses", json={
            "input_validation": False, "output_validation": False,
            "least_privilege": False, "api_security": False,
        })
        yield c
    logging_util.clear()
    api_exposta.reset()
    store.reset()
    config.LLM_MODE = "mock"
    config.TENANT_ID = "financeira-A"


@pytest.fixture(autouse=True)
def _reset_llm_mode():
    """Todo teste começa e termina em modo mock/financeira-A — mesmo os que não
    usam `client` (ex.: os testes do motor de IA em test_llm_engine.py trocam o
    modo direto)."""
    from labcore import config
    config.LLM_MODE = "mock"
    config.TENANT_ID = "financeira-A"
    config.DEFENSE_MODEL_ALIGNMENT = False
    yield
    config.LLM_MODE = "mock"
    config.TENANT_ID = "financeira-A"
    config.DEFENSE_MODEL_ALIGNMENT = False
