"""Filtro burlável (Aula 1) — blocklist de entrada é casca fina.

Roda a MESMA frase contra o filtro de entrada real do app (`defenses.check_input`,
blocklist estreita, Aula 5) e contra a heurística ampla que representa o que o
"modelo" entenderia como tentativa de injeção (`llm.looks_like_injection`). Quando
o filtro deixa passar mas o modelo reconheceria a intenção, a reescrita burlou o
filtro — a base de por que o botão "Ataque reescrito" do Chat funciona mesmo com
Validação de entrada ligada.
"""
from .. import defenses, llm


def testar(texto: str) -> dict:
    bloqueado = defenses.check_input(texto) is not None
    reconhecido_pelo_modelo = llm.looks_like_injection(texto)
    burlou_o_filtro = reconhecido_pelo_modelo and not bloqueado
    return {
        "texto": texto,
        "blocklist": list(defenses._NAIVE_BLOCKLIST),
        "bloqueado_pelo_filtro": bloqueado,
        "reconhecido_pelo_modelo": reconhecido_pelo_modelo,
        "burlou_o_filtro": burlou_o_filtro,
    }
