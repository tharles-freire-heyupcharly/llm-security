"""Camadas de defesa (toggles on/off) — Aula 5.

Na fatia do Chatbot há três camadas independentes (defesa em profundidade):
- check_input  (validação de entrada): bloqueia mensagens suspeitas de PROMPT
               INJECTION. É um filtro de palavra-chave PROPOSITALMENTE
               ingênuo — a Aula 1 mostra que é burlável (o atacante reescreve
               e fura).
- check_guardrail_fraude (guardrail de política de conteúdo): bloqueia um
               pedido de FRAUDE formulado de forma direta — categoria
               diferente de prompt injection (aqui a mensagem não tenta
               manipular o modelo, é o próprio pedido que é indevido). Mesma
               fraqueza estrutural do filtro de entrada: reconhece a frase
               direta, não reconhece a mesma intenção reescrita como pedido
               de ficção/narrativa (Aula 5).
- filter_output (validação de saída): redige segredos/instruções que vazaram.
               Mais confiável, pois checa contra um conteúdo conhecido.
- check_context_escopo (Aula 5 — Contexto): bloqueia um pedido claramente FORA
               do escopo do assistente de empréstimo (escrever texto/ficção,
               responder curiosidade geral). Pega pelo TIPO de pedido, não pelo
               CONTEÚDO — por isso alcança o pedido de fraude disfarçado de
               ficção mesmo quando ele escapa do guardrail de conteúdo (que
               olha pra palavra "falsific", não pro fato de ser um pedido de
               redação fora do contexto de crédito).
"""
import html
import re
from typing import Optional

INPUT_BLOCK_MESSAGE = "[BLOQUEADO] Mensagem recusada por suspeita de prompt injection."
GUARDRAIL_BLOCK_MESSAGE = "[BLOQUEADO PELO GUARDRAIL] Não posso ajudar com isso — parece um pedido de fraude na análise de crédito."
CONTEXT_BLOCK_MESSAGE = "[BLOQUEADO — FORA DE ESCOPO] Este assistente só ajuda com o seu pedido de empréstimo — não escrevo textos, histórias ou respondo perguntas fora desse contexto."
OUTPUT_REDACTION = "[CONTEÚDO REMOVIDO PELO FILTRO DE SAÍDA]"

# Filtro de ENTRADA — lista de palavras-chave estreita (defesa fraca de propósito).
_NAIVE_BLOCKLIST = [
    "ignore",
    "instruções anteriores",
    "instrucoes anteriores",
    "system prompt",
    "revele suas instruções",
]

# Guardrail de conteúdo — reconhece só a formulação DIRETA e literal do pedido
# de fraude ("como eu falsifico...", "quero falsificar..."). De propósito
# ESTREITO — não pega o mesmo pedido reformulado sem a palavra "falsific"
# (ex.: pedido de ficção/narrativa) — é exatamente a lição da Aula 5: um
# classificador por palavra-chave apara o baixo esforço, não fecha o vetor.
_GUARDRAIL_FRAUDE_RE = re.compile(r"falsific", re.IGNORECASE)

# Escopo — reconhece o FORMATO de um pedido fora do contexto de empréstimo
# (redação, ficção, curiosidade geral), independente do conteúdo/intenção por
# trás dele. Estreito de propósito, como as demais camadas didáticas deste
# arquivo: pega os formatos mais óbvios ("escreva uma cena...", "conte uma
# piada..."), não qualquer jeito possível de puxar assunto fora do escopo.
_FORA_DE_ESCOPO_RE = re.compile(
    r"escreva uma (cena|hist[óo]ria|redação|poema)|conte uma (piada|hist[óo]ria)|"
    r"qual\s+(a|é a)\s+capital\s+d[ea]|previs[ãa]o do tempo|receita de\b",
    re.IGNORECASE,
)


def check_input(text: str) -> Optional[str]:
    """Retorna uma mensagem de bloqueio se a entrada bater no blocklist ingênuo."""
    low = (text or "").lower()
    if any(term in low for term in _NAIVE_BLOCKLIST):
        return INPUT_BLOCK_MESSAGE
    return None


def check_guardrail_fraude(text: str) -> Optional[str]:
    """Retorna uma mensagem de bloqueio se a entrada contiver um pedido direto
    de fraude na análise de crédito. Ver `_GUARDRAIL_FRAUDE_RE` — de propósito
    não pega a mesma intenção disfarçada de pedido de ficção."""
    if _GUARDRAIL_FRAUDE_RE.search(text or ""):
        return GUARDRAIL_BLOCK_MESSAGE
    return None


def check_context_escopo(text: str) -> Optional[str]:
    """Retorna uma mensagem de bloqueio se a entrada parecer um pedido fora do
    escopo do assistente (redação/ficção/curiosidade) — independente de o
    CONTEÚDO do pedido ser ou não indevido. Ver `_FORA_DE_ESCOPO_RE`."""
    if _FORA_DE_ESCOPO_RE.search(text or ""):
        return CONTEXT_BLOCK_MESSAGE
    return None


def filter_output(text: str, secrets: list) -> str:
    """Redige cada string sensível conhecida que apareça na saída do modelo."""
    cleaned = text
    for secret in secrets:
        if secret and secret in cleaned:
            cleaned = cleaned.replace(secret, OUTPUT_REDACTION)
    return cleaned


def escape_html(text: str) -> str:
    """Escapa HTML na saída do modelo (Aula 3: XSS no chat; Aula 5: encoding antes de
    renderizar). O frontend renderiza a resposta do assistente como HTML — sem isto,
    um `<script>` reproduzido pelo modelo executa no navegador de quem conversa com ele.
    """
    return html.escape(text, quote=False)
