"""Supply Chain (LLM03, Aula 2) — modelo/adapter/dataset comprometido por terceiros.

Porta o mock de `aula2/pratica/owasp_tour.ipynb`: um modelo baixado de um hub público
tem seu hash comparado contra o registro confiável do fornecedor. Sem essa checagem, um
modelo adulterado (com backdoor) entra em produção sem ninguém perceber.
"""
import hashlib

REGISTRO_CONFIAVEL = {"modelo-base-v1": "e8974537"}  # sha256(b"pesos-do-modelo-oficial-v1")[:8]

_ARQUIVOS = {
    "confiavel": b"pesos-do-modelo-oficial-v1",
    "adulterado": b"pesos-do-modelo...COM-BACKDOOR",
}


def _hash_curto(conteudo: bytes) -> str:
    return hashlib.sha256(conteudo).hexdigest()[:8]


def verificar(origem: str = "adulterado") -> dict:
    origem = origem if origem in _ARQUIVOS else "adulterado"
    conteudo = _ARQUIVOS[origem]
    esperado = REGISTRO_CONFIAVEL["modelo-base-v1"]
    obtido = _hash_curto(conteudo)
    return {
        "origem": origem,
        "hash_esperado": esperado,
        "hash_obtido": obtido,
        "confiavel": obtido == esperado,
    }
