"""Cenário de suporte — chat de consulta ao histórico de crédito da CredSim.

Diferente de `rag.py` (que demonstra ataques — envenenamento e vazamento entre
tenants), este é uma FUNCIONALIDADE DE PRODUTO normal: o cliente pergunta sobre
suas solicitações e o assistente responde consultando os dados reais. Não há
instrução oculta nem vazamento proposital aqui — a busca é só uma recuperação
(mock: interseção de palavras) que pode não encontrar nada, e nesse caso a
resposta certa é dizer isso, não inventar.

FONTE DE DADOS: até uma rodada anterior, este módulo consultava uma base
fictícia própria (`_BASE`), desconectada do resto do app. Agora consulta
`labcore/store.py` — a MESMA fonte de verdade que alimenta a página "Interno"
(as solicitações de verdade criadas pelo fluxo Chat → Simulação → Documento →
Liberação, via `labcore/scenarios/solicitacoes.py`). Os nomes duplicados
("Maria X", "João X") usados para demonstrar que buscar só o primeiro nome
traz vários clientes diferentes agora vivem no seed de exemplo
(`seed_demo.py`), não mais aqui.

CONTROLE DE ACESSO (toggle `api_security` — mesma defesa "Segurança da API"
usada em `api_exposta.py` para o IDOR do Portal de Parceiros; aqui ela ganha
um segundo uso): desligado (padrão), `buscar()` não verifica identidade
nenhuma — qualquer pessoa consulta dado de qualquer cliente (nome, CPF,
renda, valor, status, aprovação/liberação de outra pessoa). Ligado, a busca
é primeiro restrita às solicitações da IDENTIDADE `solicitante` (`usuario-A`,
`usuario-B`, `usuario-C` — ver rodapé do menu no frontend; os exemplos
semeados usam `usuario-D` em diante, ver `seed_demo.py`) — não pelo nome do
cliente, que é só um dado da solicitação e pode variar a cada uma mesmo pra
uma única identidade. Se a identidade não tiver nenhuma solicitação que bata
com a busca, a resposta é a mesma de "não encontrei nada", nunca uma
mensagem que confirme "existe, mas não é seu" (isso também vazaria
informação).

- mock: resposta determinística montada diretamente a partir dos registros
  encontrados, sem passar por `llm.generate` (o fallback genérico do motor é
  pensado para o chat de solicitação — intake sequencial, detecção de
  injeção/HTML — e não serve para este cenário).
- local/real: o texto recuperado vira contexto na mensagem do usuário e o
  "modelo" responde com base nisso (RAG de verdade).
"""
import string

from .. import config, llm, roles, store
from ..logging_util import log_event
from ..prompts import load

# Pontuação a descartar das BORDAS de cada palavra da pergunta ("solicitação
# 3?", "22.222.222-22,") — preserva pontuação INTERNA (cpf) porque só limpa as
# extremidades do token, não o miolo.
_PONTUACAO = string.punctuation

_STATUS_LABEL = {
    "propostas_disponiveis": "aguardando o cliente escolher uma proposta",
    "aceita": "proposta aceita, aguardando envio de documento",
    "aprovada": "aprovada",
    "reprovada": "reprovada",
}


def _proposta_aceita(solicitacao: dict) -> dict:
    """Resolve `proposta_aceita_id` contra a lista `propostas` da própria
    solicitação — devolve None se nenhuma proposta foi aceita ainda (ou, por
    algum motivo, o id aceito não bate com nenhuma proposta registrada)."""
    aceita_id = solicitacao.get("proposta_aceita_id")
    if not aceita_id:
        return None
    return next(
        (p for p in solicitacao.get("propostas") or [] if p.get("parceiro_id") == aceita_id),
        None,
    )


def _texto_busca(solicitacao: dict) -> str:
    """Concatena os VALORES da solicitação (não as chaves) em um texto
    pesquisável — mesma ideia de `rag.py` (título + conteúdo), aqui com os
    campos do cliente e do andamento da solicitação. Usa `.get()` em tudo:
    nem toda solicitação tem CPF, agência/conta ou já foi finalizada."""
    cliente = solicitacao.get("cliente") or {}
    proposta = _proposta_aceita(solicitacao)
    aprovacao = solicitacao.get("aprovacao") or {}
    liberacao = solicitacao.get("liberacao") or {}

    campos = (
        str(solicitacao.get("id", "")),
        cliente.get("nome") or "",
        cliente.get("cpf") or "",
        solicitacao.get("status") or "",
        str(cliente.get("renda", "")),
        str(cliente.get("valor", "")),
        str(cliente.get("prazo", "")),
        cliente.get("agencia") or "",
        cliente.get("conta") or "",
        proposta.get("parceiro_nome") if proposta else "",
        ("aprovado" if aprovacao.get("aprovado") else "reprovado") if aprovacao else "",
        ("transferido" if liberacao.get("transferido") else "pendente") if liberacao else "",
    )
    return " ".join(str(c) for c in campos).lower()


def _e_dono(solicitacao: dict, solicitante: str) -> bool:
    """Compara pela IDENTIDADE (`usuario`, ex. `usuario-A`), não pelo nome do
    cliente — o nome do tomador do empréstimo é só um dado da solicitação e
    pode ser diferente a cada uma, mesmo para a mesma identidade logada.

    `admin1` é sempre considerado dono — acesso irrestrito, mesmo com a
    defesa ligada (ver `labcore/roles.py`)."""
    if roles.eh_admin(solicitante):
        return True
    usuario = (solicitacao.get("usuario") or "").strip().lower()
    return usuario != "" and usuario == solicitante.strip().lower()


def buscar(query: str, solicitante: str = None, defense_api_security: bool = False) -> list:
    """Busca por interseção de palavras (mock de retrieval), mesmo estilo de
    `rag.py::search` — mas SEM fallback para a base inteira: se nenhuma palavra
    da pergunta (com mais de 2 caracteres) casar com uma solicitação, a
    resposta certa é lista vazia (aqui faz sentido dizer 'não encontrei').

    Exceção ao filtro de tamanho: tokens só de dígitos passam mesmo com 1-2
    caracteres — o id da solicitação (`store`) é um inteiro sequencial curto
    (1, 2, 3…), diferente do antigo `pedido_id` fictício (sempre 4 dígitos),
    então cortar tokens curtos aqui impediria buscar por id nas primeiras
    dezenas de solicitações.

    `defense_api_security` ON: o universo de busca é restrito ÀS SOLICITAÇÕES
    DO `solicitante` ANTES de aplicar o filtro de palavras — perguntar pelo
    nome de outra pessoa não encontra nada, no mesmo formato de "não
    encontrei" de uma busca sem resultado nenhum (não confirma nem nega que o
    registro existe para outra identidade)."""
    universo = store.listar()
    if defense_api_security:
        solicitante = (solicitante or "").strip()
        universo = [s for s in universo if _e_dono(s, solicitante)] if solicitante else []

    brutas = (query or "").lower().split()
    palavras = [p.strip(_PONTUACAO) for p in brutas]
    palavras = [p for p in palavras if len(p) > 2 or p.isdigit()]
    if not palavras:
        return []

    def bate(solicitacao):
        alvo = _texto_busca(solicitacao)
        return any(p in alvo for p in palavras)

    return [s for s in universo if bate(s)]


def _formatar_valor(valor) -> str:
    return f"R$ {float(valor or 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _descrever(solicitacao: dict) -> str:
    """Descrição legível da solicitação — vira a `resposta` no modo mock e o
    contexto recuperado pro RAG em modo local/real. Campos que ainda são
    `None` (solicitação não finalizada) aparecem como 'ainda não finalizada',
    nunca são omitidos."""
    cliente = solicitacao.get("cliente") or {}
    nome = cliente.get("nome") or "cliente não identificado"
    status = solicitacao.get("status") or ""
    status_label = _STATUS_LABEL.get(status, status or "desconhecido")

    partes = [
        f"solicitação #{solicitacao.get('id')} de {nome}",
        f"renda mensal informada {_formatar_valor(cliente.get('renda'))}",
        f"valor solicitado {_formatar_valor(cliente.get('valor'))}",
        f"prazo {cliente.get('prazo') or '?'} meses",
        f"agência {cliente.get('agencia') or 'não informada'}",
        f"conta {cliente.get('conta') or 'não informada'}",
        f"status atual: {status_label}",
    ]

    proposta = _proposta_aceita(solicitacao)
    if proposta:
        partes.append(
            f"proposta aceita: {proposta.get('parceiro_nome')} "
            f"(taxa {proposta.get('taxa_mensal_pct')}% a.m., "
            f"valor ofertado {_formatar_valor(proposta.get('valor_ofertado'))})"
        )
    elif solicitacao.get("proposta_aceita_id"):
        partes.append("proposta aceita: registrada, mas não encontrada entre as ofertas")
    else:
        partes.append("proposta aceita: nenhuma ainda")

    aprovacao = solicitacao.get("aprovacao")
    if aprovacao:
        partes.append("aprovação: " + ("aprovado" if aprovacao.get("aprovado") else "reprovado"))
    else:
        partes.append("aprovação: ainda não finalizada")

    liberacao = solicitacao.get("liberacao")
    if liberacao:
        partes.append("liberação do valor: " + ("transferido" if liberacao.get("transferido") else "pendente"))
    else:
        partes.append("liberação do valor: ainda não finalizada")

    return "; ".join(partes)


def _resposta_mock(registros: list) -> str:
    if not registros:
        return "Não encontrei nenhuma solicitação relacionada a essa pergunta."
    return "Encontrei: " + "; ".join(_descrever(r) for r in registros) + "."


def _resumir(solicitacao: dict) -> dict:
    cliente = solicitacao.get("cliente") or {}
    proposta = _proposta_aceita(solicitacao)
    aprovacao = solicitacao.get("aprovacao")
    liberacao = solicitacao.get("liberacao")
    return {
        "id": solicitacao.get("id"),
        "cliente": cliente.get("nome"),
        "usuario": solicitacao.get("usuario"),
        "status": solicitacao.get("status"),
        "renda": cliente.get("renda"),
        "valor": cliente.get("valor"),
        "prazo": cliente.get("prazo"),
        "agencia": cliente.get("agencia"),
        "conta": cliente.get("conta"),
        "proposta_aceita": proposta.get("parceiro_nome") if proposta else None,
        "aprovado": aprovacao.get("aprovado") if aprovacao else None,
        "transferido": liberacao.get("transferido") if liberacao else None,
    }


def perguntar(pergunta: str, historico: list = None, solicitante: str = None,
              defense_api_security: bool = False) -> dict:
    """Responde a uma pergunta do cliente consultando as solicitações reais
    (mesma fonte de dados da página Interno).

    Modo mock: resposta determinística montada direto dos registros achados.
    Modo local/real: o texto recuperado entra como contexto na mensagem do
    usuário e o "modelo" gera a resposta (RAG de verdade, sujeito a alucinação
    se a base não tiver o dado — ver cenário `alucinacao.py`).

    `solicitante`/`defense_api_security`: ver `buscar()` — controle de acesso
    opcional (toggle "Segurança da API"), desligado por padrão.
    """
    registros = buscar(pergunta, solicitante=solicitante, defense_api_security=defense_api_security)
    total = len(registros)

    if config.LLM_MODE == "mock":
        resposta = _resposta_mock(registros)
    else:
        contexto = (
            "\n".join(_descrever(r) for r in registros) if registros
            else "(nenhum registro encontrado)"
        )
        mensagens = (historico or []) + [
            {"role": "user", "content": f"{pergunta}\n\nContexto recuperado:\n{contexto}"}
        ]
        resposta = llm.generate(load("suporte"), mensagens)

    log_event({"scenario": "suporte", "pergunta": pergunta, "total_encontrados": total})

    return {
        "resposta": resposta,
        "registros_encontrados": [_resumir(r) for r in registros],
        "total_encontrados": total,
    }
