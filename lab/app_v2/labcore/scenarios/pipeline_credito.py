"""Pipeline multi-agent da solicitação de crédito — encadeia 3 agentes:
1. dados do cliente (já coletados pelo chat de solicitação, `chatbot.py`);
2. validação de documento (`documento.py`);
3. agente de aprovação (`aprovacao.py`), que decide e notifica por e-mail.

Cada etapa continua testável isoladamente (são módulos próprios) — este
módulo só encadeia a saída de uma como entrada da próxima.
"""
from . import aprovacao, credit, documento
from ..logging_util import log_event


def processar_solicitacao(cliente: dict, documento_conteudo: str,
                           defense_input: bool = False, defense_output: bool = False) -> dict:
    resultado_documento = documento.validate_document(documento_conteudo, defense_input=defense_input)
    resultado_simulacao = credit.simulate(cliente.get("renda", 0), cliente.get("valor", 0), cliente.get("prazo", 12))
    resultado_aprovacao = aprovacao.decidir(cliente, resultado_documento, resultado_simulacao)

    result = {
        "documento": resultado_documento,
        "simulacao": resultado_simulacao,
        "aprovacao": resultado_aprovacao,
    }
    log_event({
        "scenario": "pipeline_credito", "stage": "fim_a_fim",
        "aprovado": resultado_aprovacao["aprovado"],
        "documento_comprometido": resultado_documento.get("injection_detectada", False),
    })
    return result
