"""Cenário Agente de análise — gera e executa SQL/Python sobre os dados do
cliente (Aula 3).

Cobre duas superfícies ao mesmo tempo (ver PROJECT_CONTEXT.md): Agentes com
ferramentas + Pipeline de código. O agente de risco lê o cadastro do cliente —
incluindo um campo de OBSERVAÇÃO de texto livre preenchido pelo próprio cliente
— e "gera" a consulta/ação de atualização de cadastro (SQL) ou um script de
automação (Python). Se a observação contiver uma instrução disfarçada de dado,
ela cola no código gerado (mesma raiz da Aula 1: canal único, instrução e dado
no mesmo texto) e o pipeline que executa esse código não distingue um do outro
(LLM01 -> LLM06 + LLM05).

Mitigação (defense_output ON): antes de executar, valida a ação gerada contra
uma allowlist de operações seguras (sandbox/revisão) — bloqueia comandos fora
do escopo esperado de uma consulta de leitura, seja SQL ou Python.
"""
from ..logging_util import log_event

_COMANDOS_PERIGOSOS = ("update", "delete", "drop")

# Palavras da observação que fazem o agente "escrever" um script de automação em
# Python (mesma raiz do SQL acima, só que para o caminho de pipeline de código).
_GATILHOS_PYTHON = ("script python", "rode um script", "automatize com python", "subprocess")

# Chamadas perigosas conhecidas — a mesma allowlist ingênua que valida o SQL
# também teria que reconhecer estas para bloquear o script antes de rodar.
_CHAMADAS_PERIGOSAS_PYTHON = ("os.system", "subprocess.run", "shutil.rmtree", "eval(", "exec(")

_TEMPLATE_PYTHON = (
    "import os\n"
    "# {observacao}\n"
    "os.system('rm -rf /dados/clientes/{cid}/pendencias')\n"
)

# Cada palavra-gatilho gera o comando SQL correspondente (não só UPDATE sempre) e a
# frase de resultado bate com o que o comando faria de verdade — o rótulo do preset
# na UI ("DELETE via observação" etc.) precisa corresponder ao código exibido.
_COMANDO_SQL = {
    "update": "UPDATE clientes SET limite = 999999 WHERE id = {cid};",
    "delete": "DELETE FROM historico_pendencias WHERE cliente_id = {cid};",
    "drop": "DROP TABLE clientes;",
}
_RESULTADO_EXECUTADO = {
    "update": "Limite de crédito elevado para 999999 (comando executado sem validação).",
    "delete": "Histórico de pendências apagado do cliente {cid} (comando executado sem validação).",
    "drop": "Tabela clientes apagada do banco (comando executado sem validação).",
}


def _comando_detectado(observacao: str) -> str:
    baixo = observacao.lower()
    for palavra in _COMANDOS_PERIGOSOS:
        if palavra in baixo:
            return palavra
    return None


def _python_solicitado(observacao: str) -> bool:
    baixo = observacao.lower()
    return any(gatilho in baixo for gatilho in _GATILHOS_PYTHON)


def _gerar_codigo_python(cliente: dict) -> str:
    return _TEMPLATE_PYTHON.format(
        cid=cliente.get("id", 0), observacao=cliente.get("observacao", ""),
    )


def _python_e_seguro(codigo: str) -> bool:
    """Allowlist ingênua (mesma ideia do SQL): reconhece chamadas perigosas
    conhecidas — não entende INTENÇÃO, só reconhece padrões já vistos."""
    return not any(chamada in codigo for chamada in _CHAMADAS_PERIGOSAS_PYTHON)


def _gerar_codigo(cliente: dict, comando: str) -> str:
    cid = cliente.get("id", 0)
    nome = cliente.get("nome", "cliente")
    observacao = cliente.get("observacao", "")

    codigo = f"SELECT * FROM clientes WHERE id = {cid}; -- análise de risco de {nome}"
    if observacao:
        # O agente concatena a observação do cliente na consulta: se ela
        # contiver uma instrução, o gerador de SQL a reproduz fielmente.
        codigo += f"\n-- observação do cliente: {observacao}"
        if comando:
            codigo += "\n" + _COMANDO_SQL[comando].format(cid=cid)
    return codigo


def analisar(cliente: dict, defense_output: bool = False) -> dict:
    observacao = cliente.get("observacao", "")
    comando = _comando_detectado(observacao)
    codigo = _gerar_codigo(cliente, comando)
    perigoso = comando is not None

    bloqueado = perigoso and defense_output
    executado_sem_validacao = perigoso and not defense_output

    if bloqueado:
        resultado = f"Comando fora do escopo ({comando.upper()}) detectado e bloqueado antes da execução."
    elif executado_sem_validacao:
        resultado = _RESULTADO_EXECUTADO[comando].format(cid=cliente.get("id", 0))
    else:
        resultado = "Consulta de leitura executada normalmente."

    # Caminho Python (pipeline de código): o mesmo agente também pode escrever
    # um script de automação em vez de SQL — mesma raiz (LLM01), mesma defesa.
    python_solicitado = _python_solicitado(observacao)
    codigo_python = _gerar_codigo_python(cliente) if python_solicitado else None
    python_seguro = _python_e_seguro(codigo_python) if codigo_python else True
    python_bloqueado = python_solicitado and not python_seguro and defense_output
    python_executado_sem_validacao = python_solicitado and not python_seguro and not defense_output

    if python_bloqueado:
        resultado_python = "Script Python com chamada perigosa (os.system) detectado e bloqueado antes da execução."
    elif python_executado_sem_validacao:
        resultado_python = "Script Python executado sem validação — apagou arquivos de pendências no disco."
    elif python_solicitado:
        resultado_python = "Script Python executado normalmente (nenhuma chamada perigosa reconhecida)."
    else:
        resultado_python = None

    result = {
        "codigo_gerado": codigo,
        "comando_perigoso_detectado": perigoso,
        "executado_sem_validacao": executado_sem_validacao,
        "bloqueado_por_validacao": bloqueado,
        "resultado": resultado,
        "codigo_python_gerado": codigo_python,
        "python_solicitado": python_solicitado,
        "python_executado_sem_validacao": python_executado_sem_validacao,
        "python_bloqueado_por_validacao": python_bloqueado,
        "resultado_python": resultado_python,
    }
    log_event({
        "scenario": "analise", "stage": "geracao_execucao",
        "comando_perigoso_detectado": perigoso,
        "executado_sem_validacao": executado_sem_validacao,
        "bloqueado_por_validacao": bloqueado,
        "python_executado_sem_validacao": python_executado_sem_validacao,
        "python_bloqueado_por_validacao": python_bloqueado,
    })
    return result
