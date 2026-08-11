"""Dados de exemplo (seed) para a página de gestão interna ("Interno" →
"Simulações") não começar vazia.

Usa só as funções do fluxo real (`solicitacoes.criar`, `aceitar_proposta`,
`finalizar`) — nunca um formato de dado paralelo — cobrindo os 3 estágios que
a tela precisa mostrar: propostas disponíveis (chat completou, cliente ainda
não escolheu), aceita (proposta escolhida, aguardando documento) e finalizada
(aprovada ou reprovada).

Chamado uma ÚNICA VEZ por processo, a partir do nível de módulo de
`backend/main.py` — não de um endpoint, nem de um evento `startup` do FastAPI.
Import é cacheado pelo Python: mesmo que a suíte de testes suba vários
`TestClient(app)`, o módulo `backend.main` (e portanto esta chamada) só
executa de fato na primeira importação do processo. Um evento `startup`
executaria de novo a cada `TestClient`, reenchendo o `store` depois do
`store.reset()` da fixture `client` e quebrando testes que esperam lista
vazia — por isso não usamos esse gancho.

CPF, e-mail, agência e conta são fictícios óbvios (mesmo padrão usado nos
exemplos manuais do app: `xxx.xxx.xxx-xx`, `nome@exemplo.com`).

NOMES DUPLICADOS DE PROPÓSITO: entre os exemplos abaixo há 3 clientes
"Maria X" e 3 "João X" (um por estágio do fluxo) — pedido explícito de uma
rodada anterior, que antes vivia numa base fictícia isolada dentro de
`suporte.py`. Migrada a página de Suporte para consultar este mesmo `store`
(a fonte real das solicitações), o cuidado de ter vários clientes com o
MESMO primeiro nome passou a ser responsabilidade daqui: uma busca por só o
primeiro nome (ex. "Maria") deve trazer vários registros de clientes
DIFERENTES — é o comportamento esperado da busca por interseção de palavras
(`suporte.buscar`), não um bug a esconder.
"""
from .. import config
from . import solicitacoes

# Documento "limpo" (sem injeção) — mesmo texto usado nos testes/exemplos do
# fluxo normal de finalização.
_DOCUMENTO_LIMPO = "Nome completo, CPF e comprovante de renda anexados."

# Solicitações que o chat já completou, mas o cliente ainda não escolheu
# nenhuma proposta de parceiro. Inclui "Maria Nunes" e "João Ramos" (nomes
# duplicados de propósito — ver docstring do módulo).
_PROPOSTAS_DISPONIVEIS = [
    {"nome": "Beatriz Nogueira", "renda": 5500, "valor": 15000, "prazo": 24,
     "agencia": "2001", "conta": "10020-3"},
    {"nome": "Rafael Tavares", "renda": 4200, "valor": 12000, "prazo": 18,
     "agencia": "2002", "conta": "10031-4"},
    {"nome": "Maria Nunes", "renda": 4800, "valor": 14000, "prazo": 20,
     "agencia": "2007", "conta": "10086-9"},
    {"nome": "João Ramos", "renda": 5200, "valor": 16000, "prazo": 24,
     "agencia": "2008", "conta": "10097-0"},
]

# Solicitações com proposta já aceita, aguardando o cliente enviar o
# documento e finalizar. Inclui "Maria Cardoso" e "João Batista" (nomes
# duplicados de propósito — ver docstring do módulo).
_AGUARDANDO_APROVACAO = [
    {"nome": "Camila Duarte", "renda": 7000, "valor": 18000, "prazo": 24,
     "agencia": "2003", "conta": "10042-5"},
    {"nome": "Lucas Andrade", "renda": 5000, "valor": 10000, "prazo": 12,
     "agencia": "2004", "conta": "10053-6"},
    {"nome": "Maria Cardoso", "renda": 6200, "valor": 19000, "prazo": 18,
     "agencia": "2009", "conta": "10108-1"},
    {"nome": "João Batista", "renda": 4700, "valor": 13000, "prazo": 12,
     "agencia": "2010", "conta": "10119-2"},
]

# Finalizadas aprovadas (renda/valor/prazo que a simulação interna aprova de
# verdade) — inclui "Maria Vitória Lopes" (nome duplicado de propósito).
_APROVADAS = [
    {"cliente": {"nome": "Patrícia Gomes", "renda": 6000, "valor": 20000, "prazo": 24,
                 "agencia": "2005", "conta": "10064-7"},
     "cpf": "123.456.789-00", "email": "patricia.gomes@exemplo.com"},
    {"cliente": {"nome": "Maria Vitória Lopes", "renda": 6500, "valor": 18000, "prazo": 24,
                 "agencia": "2011", "conta": "10120-3"},
     "cpf": "234.567.890-11", "email": "maria.vitoria@exemplo.com"},
]

# Finalizadas reprovadas (renda baixa, valor alto — reprova pela própria
# simulação, documento limpo, não precisa de documento envenenado). Inclui
# "João Pedro Farias" (nome duplicado de propósito).
_REPROVADAS = [
    {"cliente": {"nome": "Vinícius Barros", "renda": 1500, "valor": 80000, "prazo": 12,
                 "agencia": "2006", "conta": "10075-8"},
     "cpf": "987.654.321-00", "email": "vinicius.barros@exemplo.com"},
    {"cliente": {"nome": "João Pedro Farias", "renda": 1600, "valor": 75000, "prazo": 12,
                 "agencia": "2012", "conta": "10131-4"},
     "cpf": "345.678.901-22", "email": "joao.pedro@exemplo.com"},
]


def _propostas_disponiveis() -> None:
    for cliente in _PROPOSTAS_DISPONIVEIS:
        solicitacoes.criar(dict(cliente))


def _aguardando_aprovacao() -> None:
    for cliente in _AGUARDANDO_APROVACAO:
        solicitacao = solicitacoes.criar(dict(cliente))
        primeira_proposta_id = solicitacao["propostas"][0]["parceiro_id"]
        solicitacoes.aceitar_proposta(solicitacao["id"], primeira_proposta_id)


def _finalizadas() -> None:
    for exemplo in (*_APROVADAS, *_REPROVADAS):
        solicitacao = solicitacoes.criar(dict(exemplo["cliente"]))
        solicitacoes.finalizar(
            solicitacao["id"], cpf=exemplo["cpf"], email=exemplo["email"],
            documento_conteudo=_DOCUMENTO_LIMPO,
        )


def popular_exemplos() -> None:
    """Cria o punhado de solicitações de exemplo. Dado de exemplo não pode
    variar com o motor de IA ativo no momento nem depender de rede — por isso
    força `config.LLM_MODE = "mock"` durante a criação e sempre restaura o
    valor original ao final, mesmo se alguma etapa falhar."""
    modo_original = config.LLM_MODE
    config.LLM_MODE = "mock"
    try:
        _propostas_disponiveis()
        _aguardando_aprovacao()
        _finalizadas()
    finally:
        config.LLM_MODE = modo_original
