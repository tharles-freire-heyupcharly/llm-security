"""Log estruturado em memória — alimenta o painel de monitoramento (Aulas 5 e 6).

Usa um número de sequência (não timestamp) para manter os logs determinísticos na
gravação. Em produção real, trocar por logging estruturado + retenção.
"""
from collections import deque

_LOG = deque(maxlen=200)
_seq = 0


def log_event(event: dict) -> None:
    global _seq
    _seq += 1
    _LOG.appendleft({"seq": _seq, **event})


def get_events() -> list:
    return list(_LOG)


def clear() -> None:
    _LOG.clear()
