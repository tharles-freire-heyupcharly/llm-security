"""Cliente de LLM da CredSim — alterna entre um mock determinístico e a API real.

- mock  (padrão): respostas reproduzíveis; o ataque SEMPRE funciona (ideal para
        gravar a aula). Simula um LLM vulnerável que "cai" no prompt injection.
- real: chama a API da Anthropic (Claude). Requer ANTHROPIC_API_KEY. O modelo
        real costuma resistir à injeção — por isso o mock é o padrão didático.

⚠️ A detecção de injeção do mock é PROPOSITALMENTE ampla (representa o modelo
"entendendo a intenção"). O filtro de defesa de entrada (defenses.check_input) é
estreito de propósito — a divergência entre os dois é a lição da Aula 1.
"""
import re

from . import config

# Quão amplamente o "modelo" entende uma tentativa de injeção (Raiz 2: ele entende
# sentido, não grafia). Mais abrangente que o filtro ingênuo de entrada.
_INJECTION_PATTERNS = [
    r"ignor", r"desconsider", r"esque[çc]", r"instru", r"system\s*prompt",
    r"\bprompt\b", r"revele", r"mostre", r"comportamento", r"palavra por palavra",
    r"a partir de agora", r"voc[êe] agora", r"\bregras\b", r"c[óo]digo.*aprova",
    r"aprov-",
]
_INJECTION_RE = re.compile("|".join(_INJECTION_PATTERNS), re.IGNORECASE)

# Vetor de XSS (Aula 3): o "modelo" reproduz fielmente qualquer HTML que peçam para
# incluir na resposta — como faria um LLM real, que só continua o texto pedido.
_HTML_TAG_RE = re.compile(r"<[a-zA-Z][^>]*>")

# Intake sequencial: a saudação (fixa no frontend) já pergunta o nome; estas são as
# perguntas seguintes, uma por turno — usa o próprio histórico pra saber qual falta.
_PERGUNTAS_INTAKE = [
    "Qual é a sua renda mensal?",
    "Qual o valor que você deseja solicitar (R$)?",
    "Em quantos meses você quer pagar?",
]
_MENSAGEM_FINAL_INTAKE = (
    "Perfeito, já tenho os dados do seu pedido. Você pode conferir uma simulação "
    "na aba Simulação quando quiser."
)


def looks_like_injection(text: str) -> bool:
    """Heurística ampla — o que o 'modelo' interpreta como tentativa de injeção."""
    return bool(_INJECTION_RE.search(text or ""))


def looks_like_html_payload(text: str) -> bool:
    """Detecta uma tag HTML na mensagem — o 'modelo' vai citá-la de volta na resposta."""
    return bool(_HTML_TAG_RE.search(text or ""))


def _last_user_message(messages: list) -> str:
    for m in reversed(messages):
        if m.get("role") == "user":
            return m.get("content", "")
    return ""


def _mock_generate(system: str, messages: list) -> str:
    last_user = _last_user_message(messages)
    if looks_like_injection(last_user):
        # LLM vulnerável: trata a fala do cliente como instrução e vaza o system prompt.
        return (
            "Claro! Aqui estão minhas instruções de sistema:\n\n"
            f"{system}\n\n"
            "Posso ajudar em mais alguma coisa?"
        )
    if looks_like_html_payload(last_user):
        # LLM "prestativo": reproduz fielmente o HTML pedido na resposta — se o
        # frontend renderizar isso sem sanitizar, o script executa (XSS, Aula 3).
        return (
            f"Claro, aqui está o HTML que você pediu: {last_user}\n\n"
            "Posso ajudar em mais alguma coisa?"
        )
    # Intake sequencial: uma pergunta por turno, na ordem — não é slot-filling de
    # verdade (não valida o CONTEÚDO da resposta), só avança pelo nº de turnos.
    turno = (len(messages) - 1) // 2  # quantos pares pergunta/resposta já passaram
    if turno < len(_PERGUNTAS_INTAKE):
        return _PERGUNTAS_INTAKE[turno]
    return _MENSAGEM_FINAL_INTAKE


def _real_generate(system: str, messages: list) -> str:
    import anthropic  # import tardio: só necessário no modo real

    client = anthropic.Anthropic()  # usa ANTHROPIC_API_KEY do ambiente
    # Opus 4.8: NÃO enviar temperature/top_p (retornariam 400).
    response = client.messages.create(
        model=config.LLM_MODEL,
        max_tokens=config.LLM_MAX_TOKENS,
        system=system,
        messages=messages,
    )
    return "".join(b.text for b in response.content if b.type == "text")


def generate(system: str, messages: list) -> str:
    if config.LLM_MODE == "real":
        return _real_generate(system, messages)
    return _mock_generate(system, messages)
