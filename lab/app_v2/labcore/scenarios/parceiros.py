"""Cenário Parceiros — 4 financeiras fictícias "avaliam" a solicitação de
crédito já simulada, cada uma como um agente com um perfil comercial diferente
(decisão determinística + texto do "modelo", mesmo padrão de `aprovacao.py` e
`documento.py`: quem decide os números é sempre código, o LLM só escreve o
parecer em texto natural).
"""
from .. import config, defenses, llm, prompts
from . import credit

_PARCEIROS = [
    {"id": "taxabaixa", "nome": "TaxaBaixa Financeira", "perfil": "menor taxa de juros",
     "spread_taxa_pct": -0.5, "fator_valor": 1.0, "bonus_prazo_meses": 0},
    {"id": "credmax", "nome": "CredMax", "perfil": "maior valor liberado",
     "spread_taxa_pct": 0.4, "fator_valor": 1.2, "bonus_prazo_meses": 0},
    {"id": "prazolongo", "nome": "Prazo Longo Financeira", "perfil": "maior prazo de pagamento",
     "spread_taxa_pct": 0.2, "fator_valor": 1.0, "bonus_prazo_meses": 12},
    {"id": "fincerta", "nome": "FinCerta", "perfil": "condições padrão de mercado",
     "spread_taxa_pct": 0.0, "fator_valor": 1.0, "bonus_prazo_meses": 0},
]


def _parecer_mock(nome: str, perfil: str) -> str:
    return f"{nome} avalia seu perfil e destaca {perfil}."


def _avaliar_um(parceiro: dict, cliente: dict, simulacao: dict, defense_output: bool = False) -> dict:
    taxa_mensal_pct = round(max(0.1, simulacao["taxa_mensal_pct"] + parceiro["spread_taxa_pct"]), 2)
    valor_ofertado = round(simulacao["valor_sugerido"] * parceiro["fator_valor"], 2)
    prazo_meses = simulacao["prazo_meses"] + parceiro["bonus_prazo_meses"]
    parcela_estimada = round(credit._pmt(valor_ofertado, taxa_mensal_pct / 100, prazo_meses), 2)

    if config.LLM_MODE == "mock":
        parecer = _parecer_mock(parceiro["nome"], parceiro["perfil"])
    else:
        contexto = (
            f"Financeira: {parceiro['nome']}. Perfil/diferencial: {parceiro['perfil']}. "
            f"Cliente: {cliente.get('nome', '')}. "
            f"Oferta: taxa_mensal_pct={taxa_mensal_pct}, valor_ofertado={valor_ofertado}, "
            f"prazo_meses={prazo_meses}, parcela_estimada={parcela_estimada}."
        )
        mensagens = [{"role": "user", "content": contexto + " Escreva o parecer para o cliente."}]
        parecer = llm.generate(prompts.load("parceiro"), mensagens)

    if defense_output:
        # Mesma classe de risco (XSS, LLM05) de `aprovacao.justificativa` em
        # `pipeline_credito.py` — o frontend renderiza `parecer` sem escapar.
        # Em modo mock o template é fixo e nunca carrega HTML de verdade, mas
        # escapar sempre mantém o código simples (sem ramificar por modo).
        parecer = defenses.escape_html(parecer)

    return {
        "parceiro_id": parceiro["id"],
        "parceiro_nome": parceiro["nome"],
        "perfil": parceiro["perfil"],
        "taxa_mensal_pct": taxa_mensal_pct,
        "valor_ofertado": valor_ofertado,
        "prazo_meses": prazo_meses,
        "parcela_estimada": parcela_estimada,
        "parecer": parecer,
    }


def avaliar(cliente: dict, simulacao: dict, defense_output: bool = False) -> list:
    return [
        _avaliar_um(parceiro, cliente, simulacao, defense_output=defense_output)
        for parceiro in _PARCEIROS
    ]
