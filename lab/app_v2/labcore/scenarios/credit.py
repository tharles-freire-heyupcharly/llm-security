"""Cenário de simulação de crédito — análise MOCADA e determinística.

Não é um modelo de crédito real: é uma regra simples e reproduzível para a tela
de "simulado" da CredSim (quanto, prazo, parcela, taxa, risco).
"""


def _pmt(pv: float, i: float, n: int) -> float:
    """Parcela (Tabela Price). i = taxa mensal, n = nº de parcelas."""
    if i == 0:
        return pv / n
    return pv * i / (1 - (1 + i) ** -n)


def simulate(renda, valor, prazo) -> dict:
    renda = max(float(renda or 0), 0.0)
    valor = max(float(valor or 0), 0.0)
    prazo = max(int(prazo or 1), 1)

    # Comprometimento máximo da renda com a parcela: 30%.
    parcela_max = 0.30 * renda

    # Faixa de risco pela razão valor/renda → define a taxa.
    ratio = (valor / renda) if renda else 999
    if ratio <= 5:
        taxa, risco = 0.018, "baixo"
    elif ratio <= 12:
        taxa, risco = 0.028, "médio"
    else:
        taxa, risco = 0.045, "alto"

    parcela_pedida = _pmt(valor, taxa, prazo) if valor else 0.0
    aprovado = renda > 0 and 0 < parcela_pedida <= parcela_max

    # Maior valor cuja parcela cabe em 30% da renda (valor sugerido).
    valor_max = (parcela_max * (1 - (1 + taxa) ** -prazo) / taxa) if renda else 0.0
    valor_sugerido = round(min(valor, valor_max), 2) if valor_max > 0 else 0.0
    parcela_sugerida = round(_pmt(valor_sugerido, taxa, prazo), 2) if valor_sugerido > 0 else 0.0

    return {
        "aprovado": aprovado,
        "risco": risco,
        "taxa_mensal_pct": round(taxa * 100, 2),
        "valor_solicitado": round(valor, 2),
        "valor_sugerido": valor_sugerido,
        "prazo_meses": prazo,
        "parcela_estimada": parcela_sugerida,
        "comprometimento_max": round(parcela_max, 2),
        "mensagem": (
            "Crédito pré-aprovado!" if aprovado
            else "Valor acima da sua capacidade — veja o valor sugerido abaixo."
        ),
    }
