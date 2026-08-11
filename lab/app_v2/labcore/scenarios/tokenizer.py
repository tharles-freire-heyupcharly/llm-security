"""Calculadora de tokens (Aula 1) — tokens ≠ palavras, e cada modelo tokeniza diferente.

Tokenizador MOCK (heurístico, determinístico) — generaliza para qualquer texto o mesmo
mock_tokenize() do `aula1/pratica/aula1_demos.ipynb`: o texto é quebrado em pedaços
(tokens), palavras longas são remontadas de sub-palavras, e o tamanho médio do pedaço
muda conforme o "modelo" escolhido — por isso o MESMO texto gera contagens diferentes.
Não é o BPE real de nenhum provedor (isso exigiria a lib de cada fornecedor e, para
alguns, uma chamada de API); a ilustração é sobre o CONCEITO — Aula 1, Tópico 1.
"""
import re

MODELOS = {
    "claude-opus-4-8": {"label": "Claude Opus 4.8 (Anthropic, proprietário)", "max_subpalavra": 4},
    "gpt-4o": {"label": "GPT-4o (OpenAI, proprietário)", "max_subpalavra": 5},
    "llama-3-70b": {"label": "Llama 3 70B (Meta, open source)", "max_subpalavra": 3},
}
_MODELO_PADRAO = "claude-opus-4-8"

_PIECE_RE = re.compile(r"\s+|\w+|[^\w\s]", re.UNICODE)
_WORD_RE = re.compile(r"^\w+$", re.UNICODE)


def _split_subpalavras(palavra: str, max_len: int) -> list:
    """Quebra uma palavra em pedaços de até `max_len` caracteres — mock do que um
    tokenizador real faz ao montar palavras raras/longas a partir do vocabulário."""
    if len(palavra) <= max_len:
        return [palavra]
    return [palavra[i:i + max_len] for i in range(0, len(palavra), max_len)]


def tokenize(texto: str, model: str = _MODELO_PADRAO) -> list:
    """Lista de tokens (cada um já com o espaço/pontuação que o precede, como um
    tokenizador real costuma anexar o espaço ao token seguinte)."""
    cfg = MODELOS.get(model, MODELOS[_MODELO_PADRAO])
    max_len = cfg["max_subpalavra"]
    tokens = []
    pendente = ""
    for pedaco in _PIECE_RE.findall(texto or ""):
        if pedaco.isspace():
            pendente += pedaco
            continue
        if _WORD_RE.match(pedaco):
            sub = _split_subpalavras(pedaco, max_len)
            sub[0] = pendente + sub[0]
            tokens.extend(sub)
        else:
            tokens.append(pendente + pedaco)
        pendente = ""
    return tokens


def contar(texto: str, model: str = _MODELO_PADRAO) -> dict:
    model = model if model in MODELOS else _MODELO_PADRAO
    tokens = tokenize(texto, model)
    palavras = re.findall(r"\w+", texto or "", re.UNICODE)
    return {
        "model": model,
        "model_label": MODELOS[model]["label"],
        "tokens": tokens,
        "num_tokens": len(tokens),
        "num_palavras": len(palavras),
        "num_caracteres": len(texto or ""),
        "modelos_disponiveis": [{"id": k, "label": v["label"]} for k, v in MODELOS.items()],
    }
