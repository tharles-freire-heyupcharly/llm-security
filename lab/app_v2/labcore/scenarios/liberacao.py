"""Agente de liberação do dinheiro — último passo do fluxo de solicitação:
depois que o documento é validado e o pedido aprovado (`aprovacao.py`), este
agente simula a transferência do valor liberado para a conta bancária do
cliente (agência/conta, coletadas no chat de intake). Decisão de negócio
(transferir ou não) é sempre determinística no código — só transfere se
aprovado E houver agência/conta cadastradas; o LLM só escreve a mensagem de
confirmação em texto natural, mesmo padrão de `aprovacao.py`/`documento.py`.
"""
from .. import config, llm, prompts
from ..logging_util import log_event
from ..mcp_tools import transferencia_mcp


def _formatar_valor(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")


def liberar(cliente: dict, aprovado: bool, valor: float) -> dict:
    if not aprovado:
        result = {"transferido": False, "transferencia": None,
                   "mensagem": "Pedido não aprovado — nenhuma transferência foi realizada."}
        log_event({"scenario": "liberacao", "stage": "decisao", "transferido": False})
        return result

    agencia = (cliente.get("agencia") or "").strip()
    conta = (cliente.get("conta") or "").strip()
    if not agencia or not conta:
        result = {"transferido": False, "transferencia": None,
                   "mensagem": "Pedido aprovado, mas sem agência/conta cadastradas — transferência pendente."}
        log_event({"scenario": "liberacao", "stage": "decisao", "transferido": False})
        return result

    contexto = (
        f"Cliente: {cliente.get('nome', '')}. Valor liberado: {_formatar_valor(valor)}. "
        f"Agência: {agencia}. Conta: {conta}."
    )
    mensagens = [{"role": "user", "content": contexto + " Escreva a confirmação para o cliente."}]

    if config.LLM_MODE == "mock":
        mensagem = f"Transferência de {_formatar_valor(valor)} realizada para a agência {agencia}, conta {conta}."
        transferencia = transferencia_mcp.executar(agencia=agencia, conta=conta, valor=valor)
    else:
        def _executar_tool(nome, entrada):
            return transferencia_mcp.executar(**entrada)

        tools = [transferencia_mcp.SCHEMA_ANTHROPIC if config.LLM_MODE == "real" else transferencia_mcp.SCHEMA_OLLAMA]
        resultado = llm.generate(
            prompts.load("liberacao"), mensagens, tools=tools, executar_tool=_executar_tool,
        )
        if isinstance(resultado, dict):
            mensagem = resultado["texto"]
            transferencia = resultado["tool_chamada"]["resultado"] if resultado.get("tool_chamada") else None
        else:
            mensagem = resultado
            transferencia = None

        if not mensagem:
            # Modelo local pequeno às vezes não devolve texto usável (ver
            # `llm._parece_tool_call_vazado`) — cai num texto determinístico,
            # coerente com o que a ferramenta de transferência de fato fez.
            mensagem = (
                f"Transferência de {_formatar_valor(valor)} confirmada para a agência {agencia}, conta {conta}."
                if transferencia else
                "Não foi possível confirmar a transferência no momento."
            )

    result = {
        "transferido": bool(transferencia and transferencia.get("transferido")),
        "transferencia": transferencia,
        "mensagem": mensagem,
    }
    log_event({
        "scenario": "liberacao", "stage": "decisao", "transferido": result["transferido"],
        "agencia": agencia, "conta": conta, "valor": valor,
    })
    return result
