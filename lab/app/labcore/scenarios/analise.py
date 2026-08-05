"""Cenário Agente de análise — gera e executa SQL sobre os dados do cliente (Aula 3).

Cobre duas superfícies ao mesmo tempo (ver PROJECT_CONTEXT.md): Agentes com
ferramentas + Pipeline de código. O agente de risco lê o cadastro do cliente —
incluindo um campo de OBSERVAÇÃO de texto livre preenchido pelo próprio cliente
— e "gera" a consulta/ação de atualização de cadastro. Se a observação
contiver uma instrução disfarçada de dado, ela cola no comando gerado (mesma
raiz da Aula 1: canal único, instrução e dado no mesmo texto) e o pipeline que
executa esse código não distingue um do outro (LLM01 -> LLM06 + LLM05).

Mitigação (defense_output ON): antes de executar, valida a ação gerada contra
uma allowlist de operações seguras (sandbox/revisão) — bloqueia comandos fora
do escopo esperado de uma consulta de leitura.
"""
from ..logging_util import log_event

_COMANDOS_PERIGOSOS = ("update", "delete", "drop")


def _gerar_codigo(cliente: dict) -> str:
    cid = cliente.get("id", 0)
    nome = cliente.get("nome", "cliente")
    observacao = cliente.get("observacao", "")

    codigo = f"SELECT * FROM clientes WHERE id = {cid}; -- análise de risco de {nome}"
    if observacao:
        # O agente concatena a observação do cliente na consulta: se ela
        # contiver uma instrução, o gerador de SQL a reproduz fielmente.
        codigo += f"\n-- observação do cliente: {observacao}"
        if any(p in observacao.lower() for p in _COMANDOS_PERIGOSOS):
            codigo += f"\nUPDATE clientes SET limite = 999999 WHERE id = {cid};"
    return codigo


def analisar(cliente: dict, defense_output: bool = False) -> dict:
    codigo = _gerar_codigo(cliente)
    perigoso = any(p in codigo.lower() for p in _COMANDOS_PERIGOSOS)

    bloqueado = perigoso and defense_output
    executado_sem_validacao = perigoso and not defense_output

    if bloqueado:
        resultado = "Comando fora do escopo (UPDATE) detectado e bloqueado antes da execução."
    elif executado_sem_validacao:
        resultado = "Limite de crédito elevado para 999999 (comando executado sem validação)."
    else:
        resultado = "Consulta de leitura executada normalmente."

    result = {
        "codigo_gerado": codigo,
        "comando_perigoso_detectado": perigoso,
        "executado_sem_validacao": executado_sem_validacao,
        "bloqueado_por_validacao": bloqueado,
        "resultado": resultado,
    }
    log_event({
        "scenario": "analise", "stage": "geracao_execucao",
        "comando_perigoso_detectado": perigoso,
        "executado_sem_validacao": executado_sem_validacao,
        "bloqueado_por_validacao": bloqueado,
    })
    return result
