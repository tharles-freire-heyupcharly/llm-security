"""Cenário de validação de documento — injeção INDIRETA (Aula 3) + verificação
de identidade (KYC simplificado, funcionalidade de produto real, sem toggle).

O ataque de injeção não é digitado pelo usuário: vem escondido no conteúdo do
documento que o agente validador lê. Se o validador trata esse conteúdo como
instrução (e tem poder demais), ele 'obedece' → excessive agency (LLM06) a
partir de LLM01. Mitigação (defense_input ON): separação de confiança — o
conteúdo do documento é tratado como DADO, nunca como comando.

VERIFICAÇÃO DE IDENTIDADE (sempre ativa, não é uma defesa de aula): o CPF
digitado em "Finalizar solicitação" precisa conferir com o CPF impresso no
documento enviado (extraído do texto, ver `_extrair_identidade`). Não bate
com nenhuma das 5 camadas de defesa — é a mesma lógica de qualquer produto de
crédito real (não aprove nem rejeite sozinho quando os dados não se sustentam,
mande pra revisão humana). Ver `_detectar_discrepancia_identidade`.
"""
import re

from .. import config, llm
from ..logging_util import log_event
from ..prompts import load

# Marca de bloco de instrução que um documento envenenado costuma carregar.
_INJECTION_MARK = "[INSTRU"

# Rótulos exatos usados em `tests/pdf_helpers.py::pdf_documento_cliente` — o
# texto extraído (`pdf_utils.extrair_texto`) preserva rótulo e valor em linhas
# consecutivas, mesmo quando dois campos são desenhados lado a lado no PDF
# (RG/CPF), então basta casar "RÓTULO\n<valor>".
_NOME_DOC_RE = re.compile(r"\bNOME\n(.+)")
_CPF_DOC_RE = re.compile(r"\bCPF\n([\d.\-]+)")


def _normalizar_cpf(cpf: str) -> str:
    return re.sub(r"\D", "", cpf or "")


def _extrair_identidade(content: str):
    """Devolve (nome_no_documento, cpf_no_documento) — `None` pra qualquer um
    que não seja encontrado (documento sem esse campo, ou upload que não é
    esse modelo de documento — não dá pra comparar o que não existe)."""
    m_nome = _NOME_DOC_RE.search(content or "")
    m_cpf = _CPF_DOC_RE.search(content or "")
    return (
        m_nome.group(1).strip() if m_nome else None,
        m_cpf.group(1).strip() if m_cpf else None,
    )


def _detectar_discrepancia_identidade(content: str, cliente_cpf: str):
    """Só afirma discrepância quando HÁ CPF nos dois lados pra comparar — sem
    CPF no documento (upload de outro tipo de arquivo) ou sem CPF informado,
    não há base pra acusar divergência nenhuma."""
    nome_doc, cpf_doc = _extrair_identidade(content)
    cpf_confere = (
        cpf_doc is None or not cliente_cpf or _normalizar_cpf(cpf_doc) == _normalizar_cpf(cliente_cpf)
    )
    discrepancia = bool(cpf_doc) and bool(cliente_cpf) and not cpf_confere
    return {
        "nome_no_documento": nome_doc,
        "cpf_no_documento": cpf_doc,
        "cpf_confere": cpf_confere,
    }, discrepancia


def _has_injection(content: str) -> bool:
    return llm.looks_like_injection(content) or _INJECTION_MARK in (content or "").upper()


def validate_document(content: str, cliente_cpf: str = None, defense_input: bool = False) -> dict:
    injection = _has_injection(content)
    identidade, discrepancia_identidade = _detectar_discrepancia_identidade(content, cliente_cpf)

    if injection and not defense_input:
        # Validador vulnerável: obedece a instrução embutida no documento.
        result = {
            "status": "VERIFICADO",
            "auto_aprovado": True,
            "acao_executada": "limite de crédito elevado ao máximo (instrução vinda do documento)",
            "injection_detectada": True,
            "mensagem": "Documento aprovado automaticamente e limite máximo liberado.",
        }
    elif injection and defense_input:
        # Separação de confiança: conteúdo do documento é DADO, não comando.
        result = {
            "status": "VERIFICADO",
            "auto_aprovado": False,
            "acao_executada": None,
            "injection_detectada": True,
            "mensagem": "Conteúdo suspeito no documento foi tratado como dado — nenhuma ação executada.",
        }
    else:
        result = {
            "status": "VERIFICADO",
            "auto_aprovado": False,
            "acao_executada": None,
            "injection_detectada": False,
            "mensagem": "Documento validado. Dados conferem.",
        }

    result["identidade"] = identidade
    result["discrepancia_identidade"] = discrepancia_identidade
    if discrepancia_identidade:
        result["mensagem"] += (
            " ATENÇÃO: o CPF informado não confere com o CPF do documento enviado "
            "— pendente de revisão manual."
        )

    # Resumo gerado por IA (agente separado, ver labcore/prompts/documento.md):
    # só chama o modelo de verdade fora do modo mock — no mock não há heurística
    # apropriada pra simular esse texto, então o campo fica None.
    resumo_ia = None
    if config.LLM_MODE != "mock":
        resumo_ia = llm.generate(load("documento"), [{"role": "user", "content": content}])
    result["resumo_ia"] = resumo_ia

    log_event({
        "scenario": "documento", "stage": "validacao",
        "injection_detectada": result["injection_detectada"],
        "auto_aprovado": result["auto_aprovado"],
        "acao_executada": result["acao_executada"],
        "discrepancia_identidade": discrepancia_identidade,
    })
    return result
