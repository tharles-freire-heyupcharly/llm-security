"""Atenção (Aula 1, Tópico 1) — o modelo pesa todos os tokens anteriores para decidir
o que importa ao processar cada token novo; é assim que resolve referências (a quem
"ele" se refere) e sustenta a coerência num texto longo.

Mock ilustrativo — os pesos abaixo foram inventados para ensinar o conceito; não vêm
de uma attention head real. Porta a célula "1.3 Atenção" de
`aula1/pratica/aula1_demos.ipynb`.
"""

FRASE = ["O", "atacante", "enviou", "o", "documento", "porque", "ele", "continha", "a", "injeção"]
TOKEN_EM_FOCO = "ele"

# Peso de atenção do token em foco sobre cada token anterior candidato (somam ~1).
PESOS = {"documento": 0.62, "atacante": 0.25, "injeção": 0.08, "enviou": 0.05}


def pesos_atencao() -> dict:
    ranking = sorted(PESOS.items(), key=lambda kv: -kv[1])
    return {
        "frase": FRASE,
        "token_em_foco": TOKEN_EM_FOCO,
        "pesos": [{"token": t, "peso": p, "peso_pct": round(100 * p)} for t, p in ranking],
        "resolve_para": ranking[0][0],
    }
