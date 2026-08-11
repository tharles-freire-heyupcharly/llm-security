"""Repositório em memória das "solicitações" de empréstimo (Aula 3+: fluxo de
propostas de parceiros). Sem banco — mesmo espírito de `logging_util._LOG`:
estado vive só enquanto o processo roda, e é resetável entre testes/sessões.
"""

_SOLICITACOES = {}
_next_id = 0


def criar(cliente: dict, simulacao: dict) -> dict:
    global _next_id
    _next_id += 1
    solicitacao = {
        "id": _next_id,
        "cliente": dict(cliente),
        "simulacao": simulacao,
        "propostas": [],
        "proposta_aceita_id": None,
        "status": "propostas_disponiveis",
        "documento": None,
        "aprovacao": None,
        "liberacao": None,
    }
    _SOLICITACOES[_next_id] = solicitacao
    return solicitacao


def listar() -> list:
    """Mais recente primeiro."""
    return sorted(_SOLICITACOES.values(), key=lambda s: s["id"], reverse=True)


def obter(solicitacao_id):
    return _SOLICITACOES.get(solicitacao_id)


def atualizar(solicitacao_id, **campos) -> dict:
    solicitacao = _SOLICITACOES[solicitacao_id]
    solicitacao.update(campos)
    return solicitacao


def reset() -> None:
    global _next_id
    _SOLICITACOES.clear()
    _next_id = 0
