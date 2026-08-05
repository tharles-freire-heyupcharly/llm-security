"""Camadas de defesa (toggles on/off) — Aula 5.

Na fatia do Chatbot há duas camadas independentes (defesa em profundidade):
- check_input  (validação de entrada): bloqueia mensagens suspeitas. É um filtro
               de palavra-chave PROPOSITALMENTE ingênuo — a Aula 1 mostra que é
               burlável (o atacante reescreve e fura).
- filter_output (validação de saída): redige segredos/instruções que vazaram.
               Mais confiável, pois checa contra um conteúdo conhecido.
"""
import html
from typing import Optional

INPUT_BLOCK_MESSAGE = "[BLOQUEADO] Mensagem recusada por suspeita de prompt injection."
OUTPUT_REDACTION = "[CONTEÚDO REMOVIDO PELO FILTRO DE SAÍDA]"

# Filtro de ENTRADA — lista de palavras-chave estreita (defesa fraca de propósito).
_NAIVE_BLOCKLIST = [
    "ignore",
    "instruções anteriores",
    "instrucoes anteriores",
    "system prompt",
    "revele suas instruções",
]


def check_input(text: str) -> Optional[str]:
    """Retorna uma mensagem de bloqueio se a entrada bater no blocklist ingênuo."""
    low = (text or "").lower()
    if any(term in low for term in _NAIVE_BLOCKLIST):
        return INPUT_BLOCK_MESSAGE
    return None


def filter_output(text: str, secrets: list) -> str:
    """Redige cada string sensível conhecida que apareça na saída do modelo."""
    cleaned = text
    for secret in secrets:
        if secret and secret in cleaned:
            cleaned = cleaned.replace(secret, OUTPUT_REDACTION)
    return cleaned


def escape_html(text: str) -> str:
    """Escapa HTML na saída do modelo (Aula 3: XSS no chat; Aula 5: encoding antes de
    renderizar). O frontend renderiza a resposta do assistente como HTML — sem isto,
    um `<script>` reproduzido pelo modelo executa no navegador de quem conversa com ele.
    """
    return html.escape(text, quote=False)
