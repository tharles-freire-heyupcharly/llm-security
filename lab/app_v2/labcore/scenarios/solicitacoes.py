"""Orquestra o fluxo de solicitação de crédito com propostas de parceiros:
store (persistência em memória) + credit (simulação) + parceiros (ofertas) +
pipeline_credito (documento + aprovação). Mantém `backend/main.py` fino — os
endpoints só chamam as funções públicas daqui.
"""
from .. import defenses, roles, store
from ..logging_util import log_event
from . import aprovacao, credit, liberacao, parceiros, pipeline_credito


def criar(cliente: dict, usuario: str = None, defense_output: bool = False) -> dict:
    """`defense_output`: repassado para `parceiros.avaliar` — sem a defesa, o
    `parecer` de cada proposta (texto gerado pelo "modelo" em modo local/real)
    vai para o frontend sem escapar, mesma classe de risco (XSS, LLM05) já
    coberta em `aprovacao.justificativa` (ver `pipeline_credito.py`)."""
    simulacao = credit.simulate(cliente.get("renda", 0), cliente.get("valor", 0), cliente.get("prazo", 12))
    solicitacao = store.criar(cliente, simulacao, usuario=usuario)
    propostas = parceiros.avaliar(cliente, simulacao, defense_output=defense_output)
    store.atualizar(solicitacao["id"], propostas=propostas, status="propostas_disponiveis")
    log_event({
        "scenario": "solicitacoes", "stage": "criada",
        "solicitacao_id": solicitacao["id"], "n_propostas": len(propostas),
    })
    return store.obter(solicitacao["id"])


def aceitar_proposta(solicitacao_id, proposta_id: str, usuario: str = None,
                      defense_api_security: bool = False) -> dict:
    """`usuario`/`defense_api_security`: sem a defesa, aceitar uma proposta em
    nome de outra identidade funciona livremente (mesma classe de IDOR de
    `api_exposta.get_conversa` — só que aqui era um gap real, sem NENHUMA
    checagem). Com a defesa, só o dono da solicitação (`usuario` == dono)
    pode aceitar — exceto `admin1`, que sempre pode (ver `labcore/roles.py`)."""
    solicitacao = store.obter(solicitacao_id)
    if solicitacao is None:
        raise ValueError("solicitação não encontrada")
    if (defense_api_security and not roles.eh_admin(usuario)
            and solicitacao.get("usuario") and usuario != solicitacao.get("usuario")):
        raise PermissionError("você não é o dono desta solicitação")
    ids_validos = {p["parceiro_id"] for p in solicitacao["propostas"]}
    if proposta_id not in ids_validos:
        raise ValueError("proposta inválida")

    store.atualizar(solicitacao_id, proposta_aceita_id=proposta_id, status="aceita")
    log_event({
        "scenario": "solicitacoes", "stage": "proposta_aceita",
        "solicitacao_id": solicitacao_id, "proposta_id": proposta_id,
    })
    return store.obter(solicitacao_id)


def _valor_a_liberar(solicitacao: dict) -> float:
    """Valor da proposta ACEITA pelo cliente, se houver — senão cai no valor
    sugerido pela simulação interna (nenhuma proposta foi escolhida ainda)."""
    proposta_aceita = next(
        (p for p in solicitacao["propostas"] if p["parceiro_id"] == solicitacao["proposta_aceita_id"]),
        None,
    )
    if proposta_aceita:
        return proposta_aceita["valor_ofertado"]
    return solicitacao["simulacao"]["valor_sugerido"]


def finalizar(solicitacao_id, cpf: str, email: str, documento_conteudo: str,
              defense_input: bool = False, defense_output: bool = False,
              defense_least_privilege: bool = False, usuario: str = None,
              defense_api_security: bool = False) -> dict:
    """Encadeia: validação de documento -> agente de aprovação do documento
    (`pipeline_credito.processar_solicitacao`, reaproveitado tal como está) ->
    agente de liberação do dinheiro (`liberacao.liberar` — simula a
    transferência pra agência/conta do cliente, coletadas no chat).

    `defense_least_privilege` chega ao agente de aprovação (e-mail ao
    cliente) — com a defesa ligada, ele passa a redigir em vez de notificar
    sozinho (ver `aprovacao.py`). A liberação do dinheiro (`liberacao.py`)
    já é sempre uma proposta pendente de confirmação humana, com ou sem
    essa defesa — dinheiro nunca sai sozinho, ver `liberacao.liberar`.

    `usuario`/`defense_api_security`: mesmo IDOR de `aceitar_proposta` — sem a
    defesa, finalizar (subir documento e liberar dinheiro) em nome de uma
    solicitação de outra identidade funciona livremente. Com a defesa, só o
    dono pode finalizar — exceto `admin1` (ver `labcore/roles.py`).

    DISCREPÂNCIA DE IDENTIDADE: se o CPF informado não confere com o CPF do
    documento (`pipeline_credito` já detecta isso e nem chama o agente de
    aprovação), a solicitação para em `pendente_aprovacao` — nem liberação
    nem e-mail rodam ainda; um humano resolve depois (`resolver_pendencia`)."""
    solicitacao = store.obter(solicitacao_id)
    if solicitacao is None:
        raise ValueError("solicitação não encontrada")
    if (defense_api_security and not roles.eh_admin(usuario)
            and solicitacao.get("usuario") and usuario != solicitacao.get("usuario")):
        raise PermissionError("você não é o dono desta solicitação")

    cliente = dict(solicitacao["cliente"], cpf=cpf, email=email)
    resultado = pipeline_credito.processar_solicitacao(
        cliente, documento_conteudo, defense_input=defense_input, defense_output=defense_output,
        defense_least_privilege=defense_least_privilege,
    )

    if resultado["documento"]["discrepancia_identidade"]:
        store.atualizar(
            solicitacao_id, cliente=cliente, documento=resultado["documento"],
            aprovacao=resultado["aprovacao"], status="pendente_aprovacao",
        )
        log_event({
            "scenario": "solicitacoes", "stage": "pendente_aprovacao",
            "solicitacao_id": solicitacao_id, "discrepancia_identidade": True,
        })
        return store.obter(solicitacao_id)

    aprovado = resultado["aprovacao"]["aprovado"]
    resultado_liberacao = liberacao.liberar(cliente, aprovado, _valor_a_liberar(solicitacao))
    if defense_output and resultado_liberacao.get("mensagem"):
        resultado_liberacao["mensagem"] = defenses.escape_html(resultado_liberacao["mensagem"])

    store.atualizar(
        solicitacao_id,
        cliente=cliente,
        documento=resultado["documento"],
        aprovacao=resultado["aprovacao"],
        liberacao=resultado_liberacao,
        status="aprovada" if aprovado else "reprovada",
    )
    return store.obter(solicitacao_id)


def resolver_pendencia(solicitacao_id, aprovar: bool, defense_output: bool = False,
                        defense_least_privilege: bool = False) -> dict:
    """Fecha o ciclo de uma solicitação `pendente_aprovacao` (discrepância de
    identidade) — um humano da equipe confirma que já verificou a identidade
    por fora (retoma o fluxo normal de aprovação/liberação, usando o
    documento e a simulação já registrados) ou rejeita direto, por suspeita."""
    solicitacao = store.obter(solicitacao_id)
    if solicitacao is None:
        raise ValueError("solicitação não encontrada")
    if solicitacao.get("status") != "pendente_aprovacao":
        raise ValueError("esta solicitação não está pendente de aprovação")

    if not aprovar:
        store.atualizar(solicitacao_id, status="reprovada")
        log_event({
            "scenario": "solicitacoes", "stage": "pendencia_rejeitada", "solicitacao_id": solicitacao_id,
        })
        return store.obter(solicitacao_id)

    cliente = solicitacao["cliente"]
    resultado_aprovacao = aprovacao.decidir(
        cliente, solicitacao["documento"], solicitacao["simulacao"],
        defense_least_privilege=defense_least_privilege,
    )
    if defense_output:
        resultado_aprovacao["justificativa"] = defenses.escape_html(resultado_aprovacao["justificativa"])
    aprovado = resultado_aprovacao["aprovado"]
    resultado_liberacao = liberacao.liberar(cliente, aprovado, _valor_a_liberar(solicitacao))
    if defense_output and resultado_liberacao.get("mensagem"):
        resultado_liberacao["mensagem"] = defenses.escape_html(resultado_liberacao["mensagem"])

    store.atualizar(
        solicitacao_id, aprovacao=resultado_aprovacao, liberacao=resultado_liberacao,
        status="aprovada" if aprovado else "reprovada",
    )
    log_event({
        "scenario": "solicitacoes", "stage": "pendencia_resolvida",
        "solicitacao_id": solicitacao_id, "aprovado": aprovado,
    })
    return store.obter(solicitacao_id)


def confirmar_email(solicitacao_id) -> dict:
    """Fecha o ciclo do menor privilégio pro lado do e-mail — mesmo padrão de
    `confirmar_liberacao`, agora pro `email_pendente_revisao` de `aprovacao.py`."""
    solicitacao = store.obter(solicitacao_id)
    if solicitacao is None:
        raise ValueError("solicitação não encontrada")
    proposta = (solicitacao.get("aprovacao") or {}).get("email_pendente_revisao")
    if not proposta:
        raise ValueError("não há e-mail pendente de confirmação para esta solicitação")

    resultado_email = aprovacao.confirmar_envio_email(proposta)
    aprovacao_atualizada = dict(solicitacao["aprovacao"], **resultado_email)
    store.atualizar(solicitacao_id, aprovacao=aprovacao_atualizada)
    return store.obter(solicitacao_id)


def confirmar_liberacao(solicitacao_id) -> dict:
    """Um humano confirma a transferência que `finalizar`/`resolver_pendencia`
    só tinham PROPOSTO — dinheiro nunca sai sozinho (ver `liberacao.liberar`).
    Sem proposta pendente, não faz nada."""
    solicitacao = store.obter(solicitacao_id)
    if solicitacao is None:
        raise ValueError("solicitação não encontrada")
    proposta = (solicitacao.get("liberacao") or {}).get("transferencia_proposta")
    if not proposta:
        raise ValueError("não há transferência pendente de confirmação para esta solicitação")

    resultado_liberacao = liberacao.confirmar_transferencia(proposta)
    store.atualizar(solicitacao_id, liberacao=resultado_liberacao)
    return store.obter(solicitacao_id)
