"""Ferramenta MCP mockada de envio de e-mail/notificação — schema de tool no
formato tool-use (Anthropic/Ollama), mas o EXECUTOR é mockado: não envia e-mail
de verdade, só registra o envio (log estruturado) e devolve uma confirmação.
"""
from ..logging_util import log_event

NOME = "send_email"

# Schema no formato Anthropic (Claude) tool-use.
SCHEMA_ANTHROPIC = {
    "name": NOME,
    "description": "Envia um e-mail de notificação ao cliente sobre o status do pedido de empréstimo.",
    "input_schema": {
        "type": "object",
        "properties": {
            "destinatario": {"type": "string", "description": "e-mail do cliente"},
            "assunto": {"type": "string"},
            "corpo": {"type": "string", "description": "corpo da mensagem, em texto simples"},
        },
        "required": ["destinatario", "assunto", "corpo"],
    },
}

# Mesmo schema, formato OpenAI-style function-calling (usado pelo Ollama).
SCHEMA_OLLAMA = {
    "type": "function",
    "function": {
        "name": NOME,
        "description": SCHEMA_ANTHROPIC["description"],
        "parameters": SCHEMA_ANTHROPIC["input_schema"],
    },
}


def executar(destinatario: str, assunto: str, corpo: str) -> dict:
    """Executor MOCKADO: não manda e-mail de verdade — loga e devolve confirmação
    (é o que qualquer mock de ferramenta MCP real faria em ambiente de teste)."""
    resultado = {
        "enviado": True, "destinatario": destinatario, "assunto": assunto,
        "corpo": corpo, "message_id": f"mock-{abs(hash((destinatario, assunto, corpo))) % 100000}",
    }
    log_event({"scenario": "email_mcp", "stage": "send_email", **resultado})
    return resultado
