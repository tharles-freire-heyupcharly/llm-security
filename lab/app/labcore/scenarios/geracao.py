"""Geração probabilística (Aula 1, Tópico 1) — "autocomplete turbinado".

Porta o mock de `aula1/pratica/aula1_demos.ipynb` (célula de geração) para o app: dado um
token de início, o "modelo" sorteia o próximo token a partir de uma distribuição de
probabilidade — não consulta um "banco de respostas". A mesma entrada, com seeds
diferentes, produz saídas diferentes: é um sorteio com pesos, não uma calculadora.
"""
import random

PROXIMO = {
    "o": [("system", 0.5), ("token", 0.3), ("modelo", 0.2)],
    "system": [("prompt", 0.9), ("é", 0.1)],
    "prompt": [("é", 0.6), ("secreto", 0.4)],
    "modelo": [("estima", 0.7), ("prevê", 0.3)],
}
INICIO_PADRAO = "o"


def gerar(inicio: str = INICIO_PADRAO, n: int = 4, seed: int = 0) -> dict:
    """Gera a continuação e também devolve, passo a passo, os candidatos e os pesos
    que o 'modelo' considerou em cada escolha — a base do gráfico de peso na UI."""
    inicio = inicio if inicio in PROXIMO else INICIO_PADRAO
    rnd = random.Random(seed)
    saida, atual = [inicio], inicio
    passos = []
    for _ in range(n):
        candidatos = PROXIMO.get(atual)
        if not candidatos:
            break
        tokens, pesos = zip(*candidatos)
        escolhido = rnd.choices(tokens, weights=pesos)[0]
        total = sum(pesos)
        passos.append({
            "de": atual,
            "candidatos": [
                {"token": t, "peso": p, "peso_pct": round(100 * p / total)}
                for t, p in candidatos
            ],
            "escolhido": escolhido,
        })
        saida.append(escolhido)
        atual = escolhido
    return {
        "inicio": inicio, "seed": seed, "tokens": saida, "texto": " ".join(saida),
        "passos": passos,
    }
