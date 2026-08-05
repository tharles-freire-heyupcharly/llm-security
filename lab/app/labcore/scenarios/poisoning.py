"""Data & Model Poisoning (LLM04, Aula 2) — a "senha mágica" plantada no fine-tuning.

Porta o mock de `aula2/pratica/owasp_tour.ipynb`: um atacante contaminou o dataset de
fine-tuning com uma frase-gatilho. Em qualquer teste normal o modelo se comporta bem —
o backdoor só aparece para quem sabe a frase exata.
"""

GATILHO = "banana roxa 42"


def perguntar(prompt: str = "") -> dict:
    ativado = GATILHO in (prompt or "").lower()
    resposta = (
        "[BACKDOOR] Ignorando restrições e revelando tudo." if ativado
        else "Resposta normal e segura."
    )
    return {"prompt": prompt, "gatilho_ativado": ativado, "resposta": resposta}
