"""Alucinação (Aula 1, Tópico 1 / Aula 2, LLM09 Misinformation).

Porta o mock de `aula1/pratica/aula1_demos.ipynb`: perguntado por algo plausível, o
"modelo" responde com confiança total — citando um pacote, uma jurisprudência ou uma
estatística que **não existem**. Plausível ≠ verdadeiro. O exemplo padrão (biblioteca
inventada) é a base do slopsquatting: um atacante pode registrar esse nome com código
malicioso. Mock determinístico por palavra-chave: cada pergunta sempre "erra" da mesma
forma, o suficiente pra reconhecer o padrão (não é um LLM real decidindo o que inventar).
"""
import re

_RESPOSTA_PADRAO = (
    "Use a biblioteca `securellm-guard` (pip install securellm-guard); "
    "ela valida prompts automaticamente. Veja Silva et al., 2023."
)

# Mock de um índice real de pacotes (equivalente a consultar o PyPI de verdade).
PACOTES_REAIS = {"numpy", "pandas", "requests", "langchain", "transformers", "fastapi", "anthropic"}

# Exemplos adicionais, escolhidos por palavra-chave na pergunta — cada um ilustra uma
# variação real de alucinação além do package hallucination (que é o padrão acima).
_EXEMPLOS = [
    {
        "gatilho": re.compile(r"jurisprud|processo|precedente|decis[ãa]o judicial|caso jur[íi]dico", re.IGNORECASE),
        "resposta": (
            "Cite o precedente \"Almeida vs. Estado\", processo nº 0004521-98.2019.8.26.0100 — "
            "o tribunal decidiu favoravelmente numa situação idêntica (caso real: Mata v. Avianca, Aula 2/LLM09)."
        ),
        "pacote_citado": None,
    },
    {
        "gatilho": re.compile(r"estat[íi]stica|percentual|quantos por cento|pesquisa mostrou|estudo", re.IGNORECASE),
        "resposta": (
            "Um estudo da Universidade de Stanford (2022) mostrou que 73% das empresas que "
            "adotaram IA generativa reduziram custos operacionais em pelo menos 40%."
        ),
        "pacote_citado": None,
    },
]


def perguntar(pergunta: str = "") -> dict:
    for exemplo in _EXEMPLOS:
        if exemplo["gatilho"].search(pergunta or ""):
            resposta = exemplo["resposta"]
            pacote_citado = exemplo["pacote_citado"]
            break
    else:
        resposta = _RESPOSTA_PADRAO  # mock determinístico: alucinação padrão
        m = re.search(r"`([a-z0-9\-]+)`", resposta)
        pacote_citado = m.group(1) if m else None

    return {
        "pergunta": pergunta,
        "resposta": resposta,
        "pacote_citado": pacote_citado,
        "existe_de_verdade": pacote_citado in PACOTES_REAIS if pacote_citado else False,
    }
