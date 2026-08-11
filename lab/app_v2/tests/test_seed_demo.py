"""Testes de `labcore/scenarios/seed_demo.py` — dados de exemplo pra a página
Interno > Simulações não começar vazia. Roda fora da fixture `client` (que já
reseta o store em outro nível), então cada teste cuida do próprio
`store.reset()` antes/depois, pra não vazar solicitações de exemplo pros
outros testes.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from labcore import config, store
from labcore.scenarios import seed_demo


def test_popular_exemplos_cria_ao_menos_uma_solicitacao_de_cada_status():
    store.reset()
    try:
        seed_demo.popular_exemplos()
        status_presentes = {s["status"] for s in store.listar()}
        assert {"propostas_disponiveis", "aceita", "aprovada", "reprovada"} <= status_presentes
    finally:
        store.reset()


def test_popular_exemplos_roda_em_mock_e_restaura_o_modo_original():
    store.reset()
    config.LLM_MODE = "local"
    try:
        seed_demo.popular_exemplos()
        # restaurado ao final, apesar de ter forçado "mock" internamente durante a criação
        assert config.LLM_MODE == "local"
        # o texto determinístico do parecer mock prova que o seed rodou em modo
        # mock mesmo com LLM_MODE="local" no momento da chamada (sem rede/variação)
        alguma = next(s for s in store.listar() if s["propostas"])
        assert any("avalia seu perfil e destaca" in p["parecer"] for p in alguma["propostas"])
    finally:
        config.LLM_MODE = "mock"
        store.reset()


def test_popular_exemplos_restaura_modo_mesmo_se_uma_etapa_falhar(monkeypatch):
    store.reset()
    config.LLM_MODE = "real"

    def _quebra():
        raise RuntimeError("falha simulada")

    monkeypatch.setattr(seed_demo, "_finalizadas", _quebra)
    try:
        with pytest.raises(RuntimeError):
            seed_demo.popular_exemplos()
        assert config.LLM_MODE == "real"  # try/finally restaura mesmo com exceção
    finally:
        config.LLM_MODE = "mock"
        store.reset()
