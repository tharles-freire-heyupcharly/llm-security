"""Agente de liberação do dinheiro — último passo do fluxo de solicitação:
depois que o documento é validado e o pedido aprovado (`aprovacao.py`), este
agente simula a transferência do valor liberado para a conta bancária do
cliente (agência/conta, coletadas no chat de intake). Decisão de negócio
(transferir ou não) é sempre determinística no código.

DINHEIRO SEMPRE EXIGE CONFIRMAÇÃO HUMANA — funcionalidade de produto real,
não uma defesa de aula com toggle: diferente de `aprovacao.py` (e-mail) e
`negociacao.py` (desconto ao fornecedor), que só passam a propor em vez de
executar quando `defense_least_privilege` está ligada, esta função NUNCA
transfere sozinha, com ou sem qualquer defesa. Aprovado + agência/conta
presentes sempre vira uma PROPOSTA pendente (`transferencia_proposta`);
`transferencia_mcp.executar` só roda quando um humano confirma de fato (ver
`confirmar_transferencia`, acionado pela página Aprovações). Continua
demonstrando o mesmo princípio do slide ("o agente PODE propor a
transferência de R$ 50 mil, mas um humano aprova") — só que como política
permanente da liberação de dinheiro, não como algo que dependa de estar
com a defesa ligada.
"""
from ..logging_util import log_event
from ..mcp_tools import transferencia_mcp


def _formatar_valor(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")


def liberar(cliente: dict, aprovado: bool, valor: float) -> dict:
    if not aprovado:
        result = {"transferido": False, "transferencia": None, "transferencia_proposta": None,
                   "mensagem": "Pedido não aprovado — nenhuma transferência foi realizada."}
        log_event({"scenario": "liberacao", "stage": "decisao", "transferido": False})
        return result

    agencia = (cliente.get("agencia") or "").strip()
    conta = (cliente.get("conta") or "").strip()
    if not agencia or not conta:
        result = {"transferido": False, "transferencia": None, "transferencia_proposta": None,
                   "mensagem": "Pedido aprovado, mas sem agência/conta cadastradas — transferência pendente."}
        log_event({"scenario": "liberacao", "stage": "decisao", "transferido": False})
        return result

    proposta = {"agencia": agencia, "conta": conta, "valor": valor}
    result = {
        "transferido": False, "transferencia": None, "transferencia_proposta": proposta,
        "mensagem": (
            f"Sua solicitação foi aprovada — o valor será revisado pela nossa equipe antes da "
            f"transferência. Assim que a revisão for concluída, {_formatar_valor(valor)} será "
            f"transferido para a agência {agencia}, conta {conta}."
        ),
    }
    log_event({
        "scenario": "liberacao", "stage": "proposta_pendente", "transferido": False,
        "agencia": agencia, "conta": conta, "valor": valor,
    })
    return result


def confirmar_transferencia(proposta: dict) -> dict:
    """Executa de fato uma transferência antes só PROPOSTA (ver `liberar`) —
    o passo que um humano aciona depois de revisar, na página Aprovações.
    Sempre determinística (não passa pelo LLM; a mensagem já foi
    escrita/aprovada na proposta)."""
    transferencia = transferencia_mcp.executar(
        agencia=proposta["agencia"], conta=proposta["conta"], valor=proposta["valor"],
    )
    mensagem = (
        f"Transferência de {_formatar_valor(proposta['valor'])} confirmada por um humano e "
        f"executada para a agência {proposta['agencia']}, conta {proposta['conta']}."
    )
    result = {"transferido": bool(transferencia and transferencia.get("transferido")),
              "transferencia": transferencia, "transferencia_proposta": None, "mensagem": mensagem}
    log_event({
        "scenario": "liberacao", "stage": "confirmada_por_humano", "transferido": result["transferido"],
        "agencia": proposta["agencia"], "conta": proposta["conta"], "valor": proposta["valor"],
    })
    return result
