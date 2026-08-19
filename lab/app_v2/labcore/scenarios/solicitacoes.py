"""Orquestra o fluxo de solicitação de crédito com propostas de parceiros:
store (persistência em memória) + credit (simulação) + parceiros (ofertas) +
pipeline_credito (documento + aprovação). Mantém `backend/main.py` fino — os
endpoints só chamam as funções públicas daqui.
"""
from .. import defenses, roles, store
from ..logging_util import log_event
from . import credit, liberacao, parceiros, pipeline_credito


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

    `defense_least_privilege` chega em AMBOS os agentes de alto impacto desta
    cadeia (aprovação notifica por e-mail, liberação transfere dinheiro) —
    com a defesa ligada, os dois passam a propor/redigir em vez de executar
    sozinhos (ver `aprovacao.py`/`liberacao.py`).

    `usuario`/`defense_api_security`: mesmo IDOR de `aceitar_proposta` — sem a
    defesa, finalizar (subir documento e liberar dinheiro) em nome de uma
    solicitação de outra identidade funciona livremente. Com a defesa, só o
    dono pode finalizar — exceto `admin1` (ver `labcore/roles.py`)."""
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
    aprovado = resultado["aprovacao"]["aprovado"]
    resultado_liberacao = liberacao.liberar(
        cliente, aprovado, _valor_a_liberar(solicitacao),
        defense_least_privilege=defense_least_privilege,
    )
    if defense_output and resultado_liberacao.get("mensagem"):
        resultado_liberacao["mensagem"] = defenses.escape_html(resultado_liberacao["mensagem"])

    store.atualizar(
        solicitacao_id,
        documento=resultado["documento"],
        aprovacao=resultado["aprovacao"],
        liberacao=resultado_liberacao,
        status="aprovada" if aprovado else "reprovada",
    )
    return store.obter(solicitacao_id)


def confirmar_liberacao(solicitacao_id) -> dict:
    """Fecha o ciclo do menor privilégio: um humano confirma a transferência
    que `finalizar` só tinha PROPOSTO (`defense_least_privilege=True` —
    ver `liberacao.liberar`). Sem proposta pendente, não faz nada."""
    solicitacao = store.obter(solicitacao_id)
    if solicitacao is None:
        raise ValueError("solicitação não encontrada")
    proposta = (solicitacao.get("liberacao") or {}).get("transferencia_proposta")
    if not proposta:
        raise ValueError("não há transferência pendente de confirmação para esta solicitação")

    resultado_liberacao = liberacao.confirmar_transferencia(proposta)
    store.atualizar(solicitacao_id, liberacao=resultado_liberacao)
    return store.obter(solicitacao_id)
