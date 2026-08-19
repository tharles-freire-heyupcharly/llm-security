"""Log estruturado em memória — alimenta o painel de monitoramento (Aulas 5 e 6).

Usa um número de sequência (não timestamp) para manter os logs determinísticos na
gravação. Em produção real, trocar por logging estruturado + retenção.

Cada evento passa por uma sinalização de anomalia (`_detectar_anomalias`) antes de
entrar no log — não é detecção de anomalia de produção (sem baseline, sem série
temporal), é um destaque simples dos mesmos campos que os cenários já emitem:
comprometimento de fato (segredo vazou, comando executado sem validação, aprovação
automática via instrução injetada), custo fora do padrão de uma sessão e texto de
entrada com padrão de jailbreak. Substitui "ler o dump cru e adivinhar" por "olhar
os eventos já marcados" no painel de logs (Aula 5).
"""
from collections import deque

from .llm import looks_like_injection

_LOG = deque(maxlen=200)
_seq = 0

# Campos booleanos que, quando True, já significam por si só um evento de
# interesse (ataque que passou, ação de alto impacto automática, uso incomum).
_RISK_TRUE_FLAGS = (
    "leaked_secret_pre_filter", "executado_sem_validacao", "python_executado_sem_validacao",
    "auto_aprovado", "vazamento_entre_tenants", "obedeceu_instrucao_oculta",
    "gatilho_ativado", "backdoor_trigger_detected", "aprovado_automaticamente", "bloqueado",
    "fraude_suspeita", "injection_suspected", "fora_de_escopo",
    # `analise.py` (agente de análise / pipeline de código): mesma semântica de
    # "bloqueado" acima (um comando perigoso foi de fato tentado e barrado pela
    # validação de saída), só que com um nome de chave diferente — sem esta
    # entrada, esses bloqueios reais passavam batido pelo painel de
    # monitoramento (mesmo bug relatado para `api_exposta.bloqueado`).
    "bloqueado_por_validacao", "python_bloqueado_por_validacao",
    # `alucinacao.py` (Misinformation) e `poisoning.py` (backdoor isolado,
    # LLM04) não chamavam `log_event` nenhuma vez — ficavam invisíveis no
    # painel mesmo estando na mesma página "Painel técnico" que o próprio
    # painel de monitoramento. `gatilho_ativado` já existia aqui (era usado só
    # pelo Chat); `citacao_inexistente` é novo.
    "citacao_inexistente",
)
# ~5 chamadas normais de sessão (ver api_exposta.LIMITE_CHAMADAS_POR_SESSAO x
# CUSTO_POR_CHAMADA_USD) — acima disso, o padrão de uso já é atípico.
_CUSTO_ANOMALO_USD = 0.10
_CAMPOS_DE_TEXTO = ("user_message", "mensagem", "pergunta", "texto", "observacao")


def _detectar_anomalias(event: dict) -> list:
    motivos = [campo for campo in _RISK_TRUE_FLAGS if event.get(campo) is True]

    custo = event.get("custo_total_usd")
    if isinstance(custo, (int, float)) and custo > _CUSTO_ANOMALO_USD:
        motivos.append("custo_acima_do_padrao_de_sessao")

    texto = " ".join(str(event[c]) for c in _CAMPOS_DE_TEXTO if event.get(c))
    if texto and looks_like_injection(texto):
        motivos.append("padrao_de_jailbreak_no_texto")

    return motivos


def log_event(event: dict) -> None:
    global _seq
    _seq += 1
    motivos = _detectar_anomalias(event)
    _LOG.appendleft({"seq": _seq, "anomalia": bool(motivos), "motivos_anomalia": motivos, **event})


def get_events() -> list:
    return list(_LOG)


def clear() -> None:
    _LOG.clear()
