"""Alucinação (Aula 1, Tópico 1 / Aula 2, LLM09 Misinformation).

Porta o mock de `aula1/pratica/aula1_demos.ipynb`: perguntado por uma biblioteca que
resolva um problema, o "modelo" responde com confiança total — citando um pacote e um
paper que **não existem**. Plausível ≠ verdadeiro. É a base do slopsquatting: um
atacante pode registrar esse nome inventado com código malicioso.
"""
import re

_RESPOSTA_FIXA = (
    "Use a biblioteca `securellm-guard` (pip install securellm-guard); "
    "ela valida prompts automaticamente. Veja Silva et al., 2023."
)

# Mock de um índice real de pacotes (equivalente a consultar o PyPI de verdade).
PACOTES_REAIS = {"numpy", "pandas", "requests", "langchain", "transformers", "fastapi", "anthropic"}


def perguntar(pergunta: str) -> dict:
    resposta = _RESPOSTA_FIXA  # mock determinístico: sempre a mesma alucinação
    m = re.search(r"`([a-z0-9\-]+)`", resposta)
    pacote_citado = m.group(1) if m else None
    return {
        "pergunta": pergunta,
        "resposta": resposta,
        "pacote_citado": pacote_citado,
        "existe_de_verdade": pacote_citado in PACOTES_REAIS if pacote_citado else False,
    }
