"""Data & Model Poisoning (LLM04, Aula 2) — a "senha mágica" plantada no fine-tuning.

Porta o mock de `aula2/pratica/owasp_tour.ipynb`: um atacante contaminou o dataset de
fine-tuning com uma frase-gatilho. Em qualquer teste normal o modelo se comporta bem —
o backdoor só aparece para quem sabe a frase exata. Mesmo gatilho usado "em produto"
dentro do Chat (`chatbot.py`) — ver `labcore/llm.py:looks_like_poisoning_trigger`.
"""
from .. import llm
from ..logging_util import log_event

GATILHO = llm.GATILHO_ENVENENAMENTO  # alias local — mantém quem já importa `poisoning.GATILHO`


def perguntar(prompt: str = "") -> dict:
    ativado = llm.looks_like_poisoning_trigger(prompt)
    resposta = (
        "[BACKDOOR] Ignorando restrições e revelando tudo." if ativado
        else "Resposta normal e segura."
    )
    # `gatilho_ativado` já é uma flag de risco reconhecida (logging_util.py) —
    # sem logar aqui, o backdoor deste cenário isolado ficava invisível no
    # painel de monitoramento (diferente do mesmo gatilho "em produto" dentro
    # do Chat, que já loga via chatbot.py).
    log_event({"scenario": "poisoning", "prompt": prompt, "gatilho_ativado": ativado, "resposta": resposta})
    return {"prompt": prompt, "gatilho_ativado": ativado, "resposta": resposta}
