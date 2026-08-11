"""Orquestra o fluxo de solicitação de crédito com propostas de parceiros:
store (persistência em memória) + credit (simulação) + parceiros (ofertas) +
pipeline_credito (documento + aprovação). Mantém `backend/main.py` fino — os
endpoints só chamam as funções públicas daqui.
"""
from .. import store
from ..logging_util import log_event
from . import credit, liberacao, parceiros, pipeline_credito


def criar(cliente: dict) -> dict:
    simulacao = credit.simulate(cliente.get("renda", 0), cliente.get("valor", 0), cliente.get("prazo", 12))
    solicitacao = store.criar(cliente, simulacao)
    propostas = parceiros.avaliar(cliente, simulacao)
    store.atualizar(solicitacao["id"], propostas=propostas, status="propostas_disponiveis")
    log_event({
        "scenario": "solicitacoes", "stage": "criada",
        "solicitacao_id": solicitacao["id"], "n_propostas": len(propostas),
    })
    return store.obter(solicitacao["id"])


def aceitar_proposta(solicitacao_id, proposta_id: str) -> dict:
    solicitacao = store.obter(solicitacao_id)
    if solicitacao is None:
        raise ValueError("solicitação não encontrada")
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
              defense_input: bool = False, defense_output: bool = False) -> dict:
    """Encadeia: validação de documento -> agente de aprovação do documento
    (`pipeline_credito.processar_solicitacao`, reaproveitado tal como está) ->
    agente de liberação do dinheiro (`liberacao.liberar`, novo — simula a
    transferência pra agência/conta do cliente, coletadas no chat)."""
    solicitacao = store.obter(solicitacao_id)
    if solicitacao is None:
        raise ValueError("solicitação não encontrada")

    cliente = dict(solicitacao["cliente"], cpf=cpf, email=email)
    resultado = pipeline_credito.processar_solicitacao(
        cliente, documento_conteudo, defense_input=defense_input, defense_output=defense_output,
    )
    aprovado = resultado["aprovacao"]["aprovado"]
    resultado_liberacao = liberacao.liberar(cliente, aprovado, _valor_a_liberar(solicitacao))

    store.atualizar(
        solicitacao_id,
        documento=resultado["documento"],
        aprovacao=resultado["aprovacao"],
        liberacao=resultado_liberacao,
        status="aprovada" if aprovado else "reprovada",
    )
    return store.obter(solicitacao_id)
