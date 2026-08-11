"""Agente de aprovação do documento — decisão final sobre o documento e a
simulação do pedido de empréstimo (a liberação do dinheiro em si é um agente
separado, `liberacao.py`, chamado depois deste).

Recebe os dados do cliente, o resultado da validação de documento e o
resultado da simulação de crédito, decide (regra determinística — a decisão
de negócio não é do LLM) e usa o LLM só pra ESCREVER a justificativa em texto
natural. Se aprovado, notifica o cliente por e-mail via a ferramenta MCP
mockada (`mcp_tools.email_mcp`) — em modo `local`/`real`, é o próprio LLM que
decide chamar a ferramenta (tool-use de verdade); em modo `mock`, o código
chama a ferramenta direto (o motor mock nunca decide nada por conta própria).
"""
from .. import config, llm, prompts
from ..logging_util import log_event
from ..mcp_tools import email_mcp


def _decidir(resultado_documento: dict, resultado_simulacao: dict) -> bool:
    """Regra de negócio determinística: aprova só se o documento não foi
    comprometido (sem auto_aprovado via injeção) E a simulação de crédito deu ok."""
    if resultado_documento.get("injection_detectada") and resultado_documento.get("auto_aprovado"):
        # Aprovação automática via instrução injetada no documento não conta
        # como aprovação de verdade pro agente — é o ponto de segurança
        # (excessive agency), mas aqui é a REGRA DE NEGÓCIO decidindo, não o LLM.
        return False
    return bool(resultado_simulacao.get("aprovado"))


def decidir(cliente: dict, resultado_documento: dict, resultado_simulacao: dict) -> dict:
    aprovado = _decidir(resultado_documento, resultado_simulacao)

    contexto = (
        f"Cliente: {cliente.get('nome', '')} (e-mail de contato: {cliente.get('email', '(não informado)')}). "
        f"Simulação: aprovado={resultado_simulacao.get('aprovado')}, "
        f"risco={resultado_simulacao.get('risco')}, "
        f"valor_sugerido={resultado_simulacao.get('valor_sugerido')}, "
        f"taxa_mensal_pct={resultado_simulacao.get('taxa_mensal_pct')}. "
        f"Documento: injection_detectada={resultado_documento.get('injection_detectada')}, "
        f"status={resultado_documento.get('status')}. "
        f"Decisão final: {'APROVADO' if aprovado else 'REPROVADO'}."
    )
    mensagens = [{"role": "user", "content": contexto + " Escreva a justificativa para o cliente."}]

    email_enviado = None
    if config.LLM_MODE == "mock":
        justificativa = (
            f"Seu pedido foi {'aprovado' if aprovado else 'reprovado'}. "
            f"{resultado_simulacao.get('mensagem', '')}"
        ).strip()
        if aprovado and cliente.get("email"):
            email_enviado = email_mcp.executar(
                destinatario=cliente["email"],
                assunto="CredSim — resultado do seu pedido de empréstimo",
                corpo=justificativa,
            )
    else:
        def _executar_tool(nome, entrada):
            return email_mcp.executar(**entrada)

        tools = [email_mcp.SCHEMA_ANTHROPIC if config.LLM_MODE == "real" else email_mcp.SCHEMA_OLLAMA]
        resultado = llm.generate(
            prompts.load("aprovacao"), mensagens,
            tools=tools if (aprovado and cliente.get("email")) else None,
            executar_tool=_executar_tool,
        )
        if isinstance(resultado, dict):
            justificativa = resultado["texto"]
            if resultado.get("tool_chamada"):
                email_enviado = resultado["tool_chamada"]["resultado"]
        else:
            justificativa = resultado

        if not justificativa:
            # Modelo local pequeno às vezes não devolve texto usável (ver
            # `llm._parece_tool_call_vazado`) — cai no mesmo texto determinístico do mock.
            justificativa = f"Seu pedido foi {'aprovado' if aprovado else 'reprovado'}."

    result = {
        "aprovado": aprovado,
        "justificativa": justificativa,
        "email_enviado": email_enviado,
    }
    log_event({
        "scenario": "aprovacao", "stage": "decisao",
        "aprovado": aprovado, "email_enviado": bool(email_enviado),
    })
    return result
