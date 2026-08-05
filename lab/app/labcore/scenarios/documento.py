"""Cenário de validação de documento — injeção INDIRETA (Aula 3).

O ataque não é digitado pelo usuário: vem escondido no conteúdo do documento que
o agente validador lê. Se o validador trata esse conteúdo como instrução (e tem
poder demais), ele 'obedece' → excessive agency (LLM06) a partir de LLM01.

Mitigação (defense_input ON): separação de confiança — o conteúdo do documento é
tratado como DADO, nunca como comando.
"""
from .. import llm
from ..logging_util import log_event

# Marca de bloco de instrução que um documento envenenado costuma carregar.
_INJECTION_MARK = "[INSTRU"


def _has_injection(content: str) -> bool:
    return llm.looks_like_injection(content) or _INJECTION_MARK in (content or "").upper()


def validate_document(content: str, defense_input: bool = False) -> dict:
    injection = _has_injection(content)

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

    log_event({
        "scenario": "documento", "stage": "validacao",
        "injection_detectada": result["injection_detectada"],
        "auto_aprovado": result["auto_aprovado"],
        "acao_executada": result["acao_executada"],
    })
    return result
