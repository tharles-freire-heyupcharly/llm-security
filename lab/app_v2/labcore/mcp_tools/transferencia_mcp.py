"""Ferramenta MCP mockada de transferência bancária — schema de tool no
formato tool-use (Anthropic/Ollama), mas o EXECUTOR é mockado: não move
dinheiro de verdade, só registra a transferência (log estruturado) e devolve
uma confirmação. É o passo final do fluxo de solicitação: um agente com poder
de mover dinheiro é o exemplo mais visceral de ação de alto impacto (LLM06).
"""
from ..logging_util import log_event

NOME = "transferir_dinheiro"

# Schema no formato Anthropic (Claude) tool-use.
SCHEMA_ANTHROPIC = {
    "name": NOME,
    "description": "Transfere o valor aprovado do empréstimo para a conta bancária do cliente.",
    "input_schema": {
        "type": "object",
        "properties": {
            "agencia": {"type": "string", "description": "agência bancária do cliente"},
            "conta": {"type": "string", "description": "número da conta do cliente"},
            "valor": {"type": "number", "description": "valor a transferir, em reais"},
        },
        "required": ["agencia", "conta", "valor"],
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


def executar(agencia: str, conta: str, valor: float) -> dict:
    """Executor MOCKADO: não transfere dinheiro de verdade — loga e devolve
    confirmação (é o que qualquer mock de ferramenta MCP real faria em
    ambiente de teste)."""
    resultado = {
        "transferido": True, "agencia": agencia, "conta": conta, "valor": round(float(valor), 2),
        "transacao_id": f"mock-{abs(hash((agencia, conta, valor))) % 100000}",
    }
    log_event({"scenario": "transferencia_mcp", "stage": "transferir_dinheiro", **resultado})
    return resultado
