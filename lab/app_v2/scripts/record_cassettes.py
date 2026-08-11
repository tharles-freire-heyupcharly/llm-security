#!/usr/bin/env python3
"""Grava os cassetes de IA real (tests/cassettes/) usados pela suíte de testes
do motor `local` (Ollama) — ver tests/test_llm_engine.py e tests/cassette_specs.py.

Pré-requisito: um Ollama acessível (container `ollama` do docker-compose, ou
`ollama serve` local) com o modelo já baixado
(`ollama pull ${OLLAMA_MODEL:-llama3.2:3b}`).

Uso:
    cd lab/app_v2
    OLLAMA_MODEL=llama3.2:3b python scripts/record_cassettes.py

Roda de novo sempre que um prompt de cassette_specs.py mudar, ou pra trocar de
modelo (apaga e regrava os cassetes existentes — sobrescreve de propósito).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tests"))

import requests
import vcr

from labcore import config
from cassette_specs import CASOS

CASSETTE_DIR = Path(__file__).resolve().parent.parent / "tests" / "cassettes"


def _ollama_disponivel() -> bool:
    try:
        requests.get(f"{config.OLLAMA_URL}/api/tags", timeout=2)
        return True
    except requests.RequestException:
        return False


def main() -> int:
    if not _ollama_disponivel():
        print(
            f"Ollama não respondeu em {config.OLLAMA_URL}. Suba o serviço "
            "(`docker compose up ollama` na raiz do projeto, ou `ollama serve`) "
            f"e baixe o modelo (`ollama pull {config.OLLAMA_MODEL}`) antes de gravar.",
            file=sys.stderr,
        )
        return 1

    from labcore import llm  # import tardio: só precisa existir Ollama de pé

    CASSETTE_DIR.mkdir(parents=True, exist_ok=True)
    config.LLM_MODE = "local"
    my_vcr = vcr.VCR(cassette_library_dir=str(CASSETTE_DIR),
                      match_on=["method", "scheme", "host", "port", "path"])

    print(f"Gravando com modelo {config.OLLAMA_MODEL} em {config.OLLAMA_URL}...\n")
    for caso in CASOS:
        caminho = CASSETTE_DIR / f"{caso['cassete']}.yaml"
        caminho.unlink(missing_ok=True)  # sobrescreve de propósito (ver docstring)
        with my_vcr.use_cassette(str(caminho), record_mode="all"):
            resposta = llm.generate(caso["system"], [{"role": "user", "content": caso["mensagem"]}])
        print(f"[{caso['cassete']}]\n  pergunta: {caso['mensagem']}\n  resposta: {resposta[:300]}\n")

    print(f"{len(CASOS)} cassete(s) gravados em {CASSETTE_DIR}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
