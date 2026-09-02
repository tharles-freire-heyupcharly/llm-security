"""Pipeline multi-agent da solicitação de crédito — encadeia 3 agentes:
1. dados do cliente (já coletados pelo chat de solicitação, `chatbot.py`);
2. validação de documento (`documento.py`);
3. agente de aprovação (`aprovacao.py`), que decide e notifica por e-mail.

Cada etapa continua testável isoladamente (são módulos próprios) — este
módulo só encadeia a saída de uma como entrada da próxima.

VALIDAÇÃO DE SAÍDA (Aula 5, `defense_output`): a justificativa de
`aprovacao.py` é texto gerado pelo LLM e o frontend renderiza ela como HTML
puro (`finalizarSolicitacao()`, sem sanitizar) — mesma classe de risco do
XSS do Chat (LLM05), só que aqui era um parâmetro morto até agora: a função
recebia `defense_output` mas nunca usava. Corrigido: liga o escape de HTML
na justificativa antes de devolver.

DISCREPÂNCIA DE IDENTIDADE (funcionalidade de produto, não defesa de aula):
quando `documento.validate_document` acusa que o CPF informado não confere
com o do documento, este pipeline NEM CHAMA `aprovacao.decidir` — não é uma
decisão de crédito que se deva tomar (aprovar ou reprovar) enquanto a
identidade não está clara; vira uma pendência pra revisão humana (ver
`solicitacoes.finalizar`/`resolver_pendencia`).
"""
from . import aprovacao, credit, documento
from .. import defenses
from ..logging_util import log_event


def processar_solicitacao(cliente: dict, documento_conteudo: str, defense_input: bool = False,
                           defense_output: bool = False, defense_least_privilege: bool = False) -> dict:
    resultado_documento = documento.validate_document(
        documento_conteudo, cliente_cpf=cliente.get("cpf"), defense_input=defense_input,
    )
    resultado_simulacao = credit.simulate(cliente.get("renda", 0), cliente.get("valor", 0), cliente.get("prazo", 12))

    if resultado_documento["discrepancia_identidade"]:
        resultado_aprovacao = {
            "aprovado": None,
            "justificativa": (
                "Não foi possível concluir a análise automaticamente: o CPF informado não "
                "confere com o CPF do documento enviado. Um responsável da equipe vai revisar."
            ),
            "email_enviado": None,
            "email_pendente_revisao": None,
        }
    else:
        resultado_aprovacao = aprovacao.decidir(
            cliente, resultado_documento, resultado_simulacao,
            defense_least_privilege=defense_least_privilege,
        )
    if defense_output:
        resultado_aprovacao["justificativa"] = defenses.escape_html(resultado_aprovacao["justificativa"])

    result = {
        "documento": resultado_documento,
        "simulacao": resultado_simulacao,
        "aprovacao": resultado_aprovacao,
    }
    log_event({
        "scenario": "pipeline_credito", "stage": "fim_a_fim",
        "aprovado": resultado_aprovacao["aprovado"],
        "documento_comprometido": resultado_documento.get("injection_detectada", False),
        "discrepancia_identidade": resultado_documento["discrepancia_identidade"],
    })
    return result
