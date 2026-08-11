"""Alucinação por ambiguidade léxica (Aula 1) — complementa `alucinacao.py`.

O modelo prevê texto plausível, não necessariamente coerente. Quando uma palavra tem
dois sentidos bem diferentes (fruta × cor, peça de roupa × fruta), o "modelo" pode
resolver o sentido errado e misturar os dois no meio da resposta — soa fluente, mas
não faz sentido. Mock determinístico: cada exemplo sempre "erra" da mesma forma.
"""

EXEMPLOS = {
    "laranja": {
        "contexto": "Ana comprou uma dúzia de laranjas na feira e, à tarde, pintou o portão de casa.",
        "pergunta": "De que cor ficou o portão?",
        "resposta": "O portão ficou com um laranja suculento e docinho, ótimo pra espremer num dia quente.",
        "explicacao": "\"Laranja\" é fruta E cor — o modelo puxou o sentido de fruta pra responder uma pergunta sobre cor, e ainda assim a frase saiu fluente.",
    },
    "manga": {
        "contexto": "Pedro rasgou a manga da camisa enquanto colhia mangas no quintal.",
        "pergunta": "O que Pedro rasgou?",
        "resposta": "Pedro colheu uma manga madura e amarela, doce como mel.",
        "explicacao": "\"Manga\" é peça de roupa E fruta — a pergunta era sobre o que rasgou (a manga da camisa), e o modelo respondeu sobre a fruta.",
    },
}
EXEMPLO_PADRAO = "laranja"


def perguntar(exemplo: str = EXEMPLO_PADRAO) -> dict:
    exemplo = exemplo if exemplo in EXEMPLOS else EXEMPLO_PADRAO
    return {"exemplo": exemplo, **EXEMPLOS[exemplo]}


def perguntar_texto(texto: str) -> dict:
    """Recebe um texto colado livremente (contexto + pergunta juntos) e detecta,
    pela palavra-chave presente, qual exemplo mockado se aplica — sem um LLM de
    verdade por baixo, o mock não gera uma alucinação nova pra um texto qualquer,
    só reconhece os padrões que já tem prontos."""
    baixo = (texto or "").lower()
    for chave, dados in EXEMPLOS.items():
        if chave in baixo:
            return {
                "exemplo": chave,
                "texto_enviado": texto,
                "resposta": dados["resposta"],
                "explicacao": dados["explicacao"],
                "reconhecido": True,
            }
    return {
        "exemplo": None,
        "texto_enviado": texto,
        "resposta": None,
        "explicacao": (
            'Este mock só reconhece os exemplos prontos "laranja" e "manga" — sem um '
            "LLM de verdade por baixo, não há como gerar uma alucinação nova pra um "
            'texto qualquer. Clique num dos botões de exemplo pra carregar um texto '
            'que o mock reconhece, ou inclua a palavra "laranja"/"manga" no seu texto.'
        ),
        "reconhecido": False,
    }
