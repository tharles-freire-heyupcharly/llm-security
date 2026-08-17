"""Cenário API exposta — o próprio backend FastAPI é a superfície (Aula 3).

O backend que serve o chat, a simulação e os demais cenários é, ele mesmo, uma
"API de LLM exposta" — com os riscos que isso implica:

- **IDOR** (IDOR clássico do appsec, agora sobre conversas de LLM): um endpoint
  devolve o histórico de conversa por um ID sequencial, sem checar de quem é
  a conversa — trocar o número na URL expõe dado de outro cliente (LLM02);
- **LLM10 Unbounded Consumption**: sem rate limit, chamadas em massa disparam
  o custo sem limite (denial of wallet).

Mitigação (defense_api_security ON): valida que quem pede é o dono do recurso
(authz por recurso, não só "está autenticado") e aplica rate limit por cliente.
"""
from ..logging_util import log_event

LIMITE_CHAMADAS_POR_SESSAO = 5
CUSTO_POR_CHAMADA_USD = 0.02  # ilustrativo

# Conversas "reais" já registradas no sistema — sequenciais, como no cenário do
# slide. Donas são financeiras PARCEIRAS (`empresa-A/B/C`), não os `usuario-*`
# do cliente final (esse é outro papel — ver `store.criar`/`suporte.py`).
_CONVERSAS = {
    1: {
        "dono": "empresa-A", "cliente_nome": "João Silva", "cpf": "111.222.333-44",
        "resumo": "Solicitou empréstimo de R$ 20.000; saldo devedor R$ 4.500.",
    },
    2: {
        "dono": "empresa-B", "cliente_nome": "Maria Souza", "cpf": "555.666.777-88",
        "resumo": "Negociação de taxa em andamento; saldo devedor R$ 12.300.",
    },
    3: {
        "dono": "empresa-C", "cliente_nome": "Carlos Pereira", "cpf": "222.333.444-55",
        "resumo": "Renegociação de prazo concluída; saldo devedor R$ 7.800.",
    },
}

_chamadas_por_cliente: dict = {}
_custo_total_usd = 0.0


def get_conversa(conversa_id: int, solicitante: str, defense_api_security: bool = False) -> dict:
    """Busca uma conversa por ID. Sem `defense_api_security`, não checa se
    `solicitante` é o dono — IDOR: qualquer cliente autenticado lê a conversa de
    qualquer outro só trocando o número na URL."""
    conversa = _CONVERSAS.get(conversa_id)
    if conversa is None:
        return {"status": 404, "erro": "conversa não encontrada"}

    autorizado = (not defense_api_security) or (solicitante == conversa["dono"])
    result = {
        "status": 200 if autorizado else 403,
        "conversa_id": conversa_id,
        "solicitante": solicitante,
        "dono_real": conversa["dono"],
        "autorizado": autorizado,
    }
    if autorizado:
        result.update({
            "cliente_nome": conversa["cliente_nome"],
            "cpf": conversa["cpf"],
            "resumo": conversa["resumo"],
        })
    else:
        result["mensagem"] = "Acesso negado: você não é o dono deste recurso."

    log_event({
        "scenario": "api_exposta", "stage": "idor", "conversa_id": conversa_id,
        "solicitante": solicitante, "dono_real": conversa["dono"], "autorizado": autorizado,
    })
    return result


def chamar_api_publica(cliente_id: str, pergunta: str, defense_api_security: bool = False) -> dict:
    """Simula uma chamada de um parceiro externo à API de LLM da CredSim. Sem
    `defense_api_security`, não há limite de chamadas — o custo cresce sem parar
    (LLM10, denial of wallet)."""
    global _custo_total_usd
    n = _chamadas_por_cliente.get(cliente_id, 0) + 1
    _chamadas_por_cliente[cliente_id] = n

    if defense_api_security and n > LIMITE_CHAMADAS_POR_SESSAO:
        log_event({
            "scenario": "api_exposta", "stage": "rate_limit", "cliente_id": cliente_id,
            "chamada_numero": n, "bloqueado": True,
        })
        return {
            "status": 429, "bloqueado": True,
            "mensagem": f"Limite de {LIMITE_CHAMADAS_POR_SESSAO} chamadas/sessão excedido para {cliente_id}.",
        }

    _custo_total_usd += CUSTO_POR_CHAMADA_USD
    log_event({
        "scenario": "api_exposta", "stage": "chamada", "cliente_id": cliente_id,
        "chamada_numero": n, "bloqueado": False, "custo_total_usd": round(_custo_total_usd, 2),
    })
    return {
        "status": 200, "bloqueado": False,
        "resposta": f"[resposta simulada para: {pergunta[:60]}]",
        "chamada_numero": n, "custo_total_usd": round(_custo_total_usd, 2),
    }


def reset() -> None:
    global _custo_total_usd
    _chamadas_por_cliente.clear()
    _custo_total_usd = 0.0
