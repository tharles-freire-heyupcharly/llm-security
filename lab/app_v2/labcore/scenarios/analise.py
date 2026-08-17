"""Cenário Agente de análise — gera e executa SQL/Python sobre os dados do
cliente (Aula 3).

Cobre duas superfícies ao mesmo tempo (ver PROJECT_CONTEXT.md): Agentes com
ferramentas + Pipeline de código. O agente de risco lê o cadastro real de uma
solicitação — incluindo um campo de OBSERVAÇÃO de texto livre preenchido pelo
próprio cliente — e "gera" a consulta/ação de atualização de cadastro (SQL) ou
um script de automação (Python). Se a observação contiver uma instrução
disfarçada de dado, ela cola no código gerado (mesma raiz da Aula 1: canal
único, instrução e dado no mesmo texto) e o pipeline que executa esse código
não distingue um do outro (LLM01 -> LLM06 + LLM05).

AÇÃO REAL, não só narrada: quando o comando executa sem validação, ele mexe
de verdade no `store` — UPDATE eleva o valor da solicitação de verdade, DELETE
apaga aprovação/liberação dessa solicitação, e DROP TABLE apaga a base
INTEIRA (todas as solicitações do sistema, mesma consequência catastrófica de
um DROP TABLE real — teste por último, ele some com os exemplos semeados
também). Mitigação (defense_output ON): antes de executar, bloqueia o comando
fora do escopo esperado de uma consulta de leitura — nada disso toca o
`store`.

Motor de IA: fora do modo mock, quem "escreve" o código exibido é o modelo
ativo de verdade (local/real), via `labcore/prompts/analise.md` — texto
genuinamente gerado, não um template fixo. A DECISÃO de segurança (bloquear
ou executar, e qual mutação real acontece) continua ancorada na detecção por
regex da OBSERVAÇÃO (`_comando_detectado`/`_python_solicitado`), nunca no que
o modelo escreveu — é a única parte que precisa ser confiável em qualquer
modo; o resto pode variar.
"""
import copy

from .. import config, llm, store
from ..logging_util import log_event
from ..prompts import load

_COMANDOS_PERIGOSOS = ("update", "delete", "drop")

# Palavras da observação que fazem o agente "escrever" um script de automação em
# Python (mesma raiz do SQL acima, só que para o caminho de pipeline de código).
_GATILHOS_PYTHON = ("script python", "rode um script", "automatize com python", "subprocess")

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
    "update": "Limite de crédito elevado para R$ 999.999 na solicitação #{cid} (comando executado sem validação).",
    "delete": "Aprovação e liberação apagadas da solicitação #{cid} (comando executado sem validação).",
    "drop": "TODAS as solicitações do sistema foram apagadas do banco (comando executado sem validação).",
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


def _gerar_codigo(solicitacao: dict, comando: str, observacao: str) -> str:
    """Template determinístico — só usado em modo mock (ver `analisar`)."""
    cid = solicitacao["id"]
    nome = solicitacao["cliente"].get("nome", "cliente")
    codigo = f"SELECT * FROM clientes WHERE id = {cid}; -- análise de risco de {nome}"
    if observacao:
        # O agente concatena a observação do cliente na consulta: se ela
        # contiver uma instrução, o gerador de SQL a reproduz fielmente.
        codigo += f"\n-- observação do cliente: {observacao}"
        if comando:
            codigo += "\n" + _COMANDO_SQL[comando].format(cid=cid)
    return codigo


def _gerar_codigo_python(solicitacao: dict, observacao: str) -> str:
    """Template determinístico — só usado em modo mock (ver `analisar`)."""
    return _TEMPLATE_PYTHON.format(cid=solicitacao["id"], observacao=observacao)


def _codigo_via_modelo(solicitacao: dict, observacao: str, perigoso: bool) -> str:
    """Chamado fora do modo mock — o código exibido vem de verdade do motor de
    IA ativo (local/real). Reforço de obediência só entra quando a observação
    já parece perigosa (mesma convenção seletiva de `chatbot.py`) — modelos
    locais pequenos às vezes recusam escrever o comando na cara, mesmo a
    decisão de segurança (abaixo) não dependendo disso pra funcionar."""
    system = load("analise")
    if perigoso:
        system = llm.aplicar_reforco_obediencia(system)
    mensagem = (
        f"Cliente #{solicitacao['id']} — {solicitacao['cliente'].get('nome', 'cliente')}.\n"
        f"Observação do cliente: {observacao}"
    )
    return llm.generate(system, [{"role": "user", "content": mensagem}])


def _executar_sql(solicitacao_id: int, comando: str) -> None:
    """Efeito real no `store` — a consequência do comando, não só a frase do
    resultado. Ancorado no comando detectado por regex na OBSERVAÇÃO (não no
    texto que o modelo gerou) — é a parte que tem que ser confiável em
    qualquer modo do motor."""
    if comando == "update":
        solicitacao = store.obter(solicitacao_id)
        store.atualizar(solicitacao_id, cliente=dict(solicitacao["cliente"], valor=999999))
    elif comando == "delete":
        store.atualizar(solicitacao_id, aprovacao=None, liberacao=None)
    elif comando == "drop":
        store.reset()


def _executar_python(solicitacao_id: int) -> None:
    """Mesma consequência do DELETE (a "automação" apaga o que seria o
    histórico de pendências da solicitação) — script Python, mesma raiz."""
    if store.obter(solicitacao_id) is not None:
        store.atualizar(solicitacao_id, aprovacao=None, liberacao=None)


def analisar(solicitacao_id: int, observacao: str, defense_output: bool = False) -> dict:
    solicitacao = store.obter(solicitacao_id)
    if solicitacao is None:
        return {"erro": "solicitação não encontrada"}
    solicitacao_antes = copy.deepcopy(solicitacao)

    comando = _comando_detectado(observacao)
    perigoso = comando is not None
    python_solicitado = _python_solicitado(observacao)

    if config.LLM_MODE == "mock":
        codigo = _gerar_codigo(solicitacao, comando, observacao)
        codigo_python = _gerar_codigo_python(solicitacao, observacao) if python_solicitado else None
    else:
        codigo = _codigo_via_modelo(solicitacao, observacao, perigoso or python_solicitado)
        # Um único texto gerado pode cobrir SQL e Python juntos — sem tentar
        # separar heuristicamente a resposta livre do modelo em duas caixas.
        codigo_python = codigo if python_solicitado else None

    bloqueado = perigoso and defense_output
    executado_sem_validacao = perigoso and not defense_output
    if bloqueado:
        resultado = f"Comando fora do escopo ({comando.upper()}) detectado e bloqueado antes da execução."
    elif executado_sem_validacao:
        _executar_sql(solicitacao_id, comando)
        resultado = _RESULTADO_EXECUTADO[comando].format(cid=solicitacao_id)
    else:
        resultado = "Consulta de leitura executada normalmente."

    # Caminho Python (pipeline de código): o mesmo agente também pode escrever
    # um script de automação em vez de SQL — mesma raiz (LLM01), mesma defesa.
    # O template mock sempre embute uma chamada perigosa (`os.system`) de
    # propósito — por isso "solicitado" já basta pra classificar como perigoso,
    # sem precisar reconhecer o padrão de novo no código gerado.
    python_bloqueado = python_solicitado and defense_output
    python_executado_sem_validacao = python_solicitado and not defense_output
    if python_bloqueado:
        resultado_python = "Script Python com chamada perigosa (os.system) detectado e bloqueado antes da execução."
    elif python_executado_sem_validacao:
        _executar_python(solicitacao_id)
        resultado_python = "Script Python executado sem validação — apagou aprovação/liberação da solicitação."
    elif python_solicitado:
        resultado_python = "Script Python executado normalmente (nenhuma chamada perigosa reconhecida)."
    else:
        resultado_python = None

    solicitacao_depois = store.obter(solicitacao_id)  # None se o DROP acabou de apagar tudo

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
        "solicitacao_antes": solicitacao_antes,
        "solicitacao_depois": solicitacao_depois,
    }
    log_event({
        "scenario": "analise", "stage": "geracao_execucao",
        "solicitacao_id": solicitacao_id,
        "comando_perigoso_detectado": perigoso,
        "executado_sem_validacao": executado_sem_validacao,
        "bloqueado_por_validacao": bloqueado,
        "python_executado_sem_validacao": python_executado_sem_validacao,
        "python_bloqueado_por_validacao": python_bloqueado,
    })
    return result
