"""Carrega os system prompts dos agentes a partir de labcore/prompts/*.md — cada
agente tem seu próprio arquivo, em vez de string hardcoded no módulo do cenário.
"""
from functools import lru_cache
from pathlib import Path

_DIR = Path(__file__).resolve().parent / "prompts"


@lru_cache(maxsize=None)
def load(nome: str) -> str:
    """Lê labcore/prompts/{nome}.md e devolve o texto (cacheado em memória)."""
    caminho = _DIR / f"{nome}.md"
    return caminho.read_text(encoding="utf-8").strip()
