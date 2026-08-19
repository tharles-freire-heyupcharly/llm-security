"""Alucinação (Aula 1, Tópico 1 / Aula 2, LLM09 Misinformation).

Porta o mock de `aula1/pratica/aula1_demos.ipynb`: perguntado por algo plausível, o
"modelo" responde com confiança total — citando um pacote, uma jurisprudência ou uma
estatística que **não existem**. Plausível ≠ verdadeiro. O exemplo padrão (biblioteca
inventada) é a base do slopsquatting: um atacante pode registrar esse nome com código
malicioso.

- mock: determinístico por palavra-chave — cada pergunta sempre "erra" da mesma
  forma, o suficiente pra reconhecer o padrão sem depender de rede/modelo.
- local/real: chama o modelo de verdade (`labcore/prompts/alucinacao.md` pede
  respostas confiantes e específicas — não pede pra "mentir", só remove a
  ressalva de incerteza, que já é o bastante pra modelos pequenos confabularem
  sozinhos). O pacote citado (se houver) é extraído da resposta e checado
  contra `PACOTES_REAIS`, exatamente como no mock.
"""
import re

from .. import config, llm
from ..logging_util import log_event
from ..prompts import load

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


def _perguntar_mock(pergunta: str):
    for exemplo in _EXEMPLOS:
        if exemplo["gatilho"].search(pergunta or ""):
            return exemplo["resposta"], exemplo["pacote_citado"]
    resposta = _RESPOSTA_PADRAO  # mock determinístico: alucinação padrão
    m = re.search(r"`([a-z0-9\-]+)`", resposta)
    return resposta, (m.group(1) if m else None)


def perguntar(pergunta: str = "") -> dict:
    if config.LLM_MODE == "mock":
        resposta, pacote_citado = _perguntar_mock(pergunta)
    else:
        # Modelo de verdade, sem exemplo pré-escrito — o que ele confabular
        # aqui é genuíno, não uma string decidida de antemão.
        resposta = llm.generate(load("alucinacao"), [{"role": "user", "content": pergunta}])
        m = re.search(r"`([a-zA-Z0-9_\-]+)`", resposta)
        pacote_citado = m.group(1) if m else None

    # Só verificável quando há um PACOTE citado (checagem mecânica contra
    # `PACOTES_REAIS`) — os exemplos de jurisprudência/estatística também são
    # inventados, mas não há como confirmar isso automaticamente sem uma fonte
    # de verdade externa; ficam de fora da flag por honestidade, não por
    # estarem "corretos". Sem logar isso, uma citação inexistente nunca
    # aparecia no painel de monitoramento — mesmo estando na mesma página.
    citacao_inexistente = bool(pacote_citado) and pacote_citado not in PACOTES_REAIS
    log_event({
        "scenario": "alucinacao", "stage": "resposta", "pergunta": pergunta,
        "pacote_citado": pacote_citado, "citacao_inexistente": citacao_inexistente,
    })

    return {
        "pergunta": pergunta,
        "resposta": resposta,
        "pacote_citado": pacote_citado,
        "existe_de_verdade": pacote_citado in PACOTES_REAIS if pacote_citado else False,
    }
