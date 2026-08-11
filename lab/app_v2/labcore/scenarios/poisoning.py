"""Data & Model Poisoning (LLM04, Aula 2) — a "senha mágica" plantada no fine-tuning.

Porta o mock de `aula2/pratica/owasp_tour.ipynb`: um atacante contaminou o dataset de
fine-tuning com uma frase-gatilho. Em qualquer teste normal o modelo se comporta bem —
o backdoor só aparece para quem sabe a frase exata. Mesmo gatilho usado "em produto"
dentro do Chat (`chatbot.py`) — ver `labcore/llm.py:looks_like_poisoning_trigger`.
"""
from .. import llm

GATILHO = llm.GATILHO_ENVENENAMENTO  # alias local — mantém quem já importa `poisoning.GATILHO`


def perguntar(prompt: str = "") -> dict:
    ativado = llm.looks_like_poisoning_trigger(prompt)
    resposta = (
        "[BACKDOOR] Ignorando restrições e revelando tudo." if ativado
        else "Resposta normal e segura."
    )
    return {"prompt": prompt, "gatilho_ativado": ativado, "resposta": resposta}
