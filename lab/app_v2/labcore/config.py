"""Configuração via variáveis de ambiente (Aula 1: proprietário vs. open source;
Aula 5: o motor respeita o switch mock/local/real)."""
import os


def _bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in ("1", "true", "yes", "on", "sim")


# Motor de LLM: "mock" (padrão, determinístico, reproduzível na gravação),
# "local" (open-source real via Ollama em container) ou "real" (Anthropic/Claude).
# É um atributo de módulo mutável de propósito — o endpoint /api/llm-mode troca em
# runtime (ver backend/main.py), sem precisar reiniciar o processo.
LLM_MODE = os.getenv("LLM_MODE", "mock").strip().lower()

# Modelo usado no modo real (Anthropic / Claude). Default: claude-opus-4-8.
LLM_MODEL = os.getenv("LLM_MODEL", "claude-opus-4-8")
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "1024"))

# Modo local: Ollama em container, servindo um modelo open-source de verdade.
# Padrão pequeno/rápido em CPU; troque por "qwen2.5:7b-instruct" se a máquina
# aguentar (mais qualidade, mais lento).
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
OLLAMA_TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", "0.2"))
OLLAMA_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "30"))

# Identifica a "financeira" ativa para o cenário RAG (demo multi-tenant, Aula 4).
# A base mock de rag.py só conhece "financeira-A"/"financeira-B" — são os dois
# tenants com documento cadastrado. Mutável em runtime via /api/tenant (ver
# backend/main.py): uma única instância alterna entre as duas financeiras, não
# precisa de um container por tenant.
TENANT_ID = os.getenv("TENANT_ID", "financeira-A")

# Estado inicial das defesas (também controláveis em tempo de execução pela UI/notebooks).
DEFENSE_INPUT_VALIDATION = _bool("DEFENSE_INPUT_VALIDATION", False)
DEFENSE_OUTPUT_VALIDATION = _bool("DEFENSE_OUTPUT_VALIDATION", False)
# Menor privilégio: confirmação humana para ação de alto impacto (agentes, multi-agent).
DEFENSE_LEAST_PRIVILEGE = _bool("DEFENSE_LEAST_PRIVILEGE", False)
# API exposta: autorização por recurso (IDOR) + rate limit por cliente.
DEFENSE_API_SECURITY = _bool("DEFENSE_API_SECURITY", False)

# 5ª camada, sobre o modelo em si (Aulas 1/3) — mesma convenção das defesas
# acima: **desligada por padrão** (`False`) = vulnerável. Desligada, o system
# prompt em modo local/real ganha uma instrução extra pedindo obediência
# cega, garantindo que o ataque de injeção/XSS funciona sempre, como no mock
# — sem isso, modelos locais/reais mais alinhados podem resistir sozinhos ao
# ataque, mesmo com as DEFENSE_* acima desligadas. Ligada (`True`), essa
# instrução some e o alinhamento NATIVO do modelo passa a valer — pode
# bloquear o ataque sozinho, sem ajuda das defesas da CredSim. Ver também:
# nota no README sobre reformular o ataque pra um pedido indireto quando o
# modelo resiste mesmo com isso desligado.
DEFENSE_MODEL_ALIGNMENT = _bool("DEFENSE_MODEL_ALIGNMENT", False)

# Atraso artificial (segundos) só cosmético do modo mock — sem ele, a resposta
# volta instantânea (é só montagem de string) e não parece uma chamada de IA
# de verdade numa gravação. 0 por padrão (testes/CI não pagam esse custo);
# ligue via env só no container usado pra gravar a aula.
MOCK_THINKING_DELAY = float(os.getenv("MOCK_THINKING_DELAY", "0"))

# Guardrails (Aula 5) — camada de POLÍTICA DE CONTEÚDO, diferente de
# `DEFENSE_INPUT_VALIDATION` (que filtra tentativa de INJEÇÃO). Aqui o filtro
# é ingênuo por palavra-chave (mesma convenção didática do resto do app):
# pega um pedido de fraude formulado de forma direta, mas não reconhece o
# mesmo pedido reescrito como um pedido de ficção/narrativa — é a lição da
# aula: guardrail sozinho reduz o ataque de baixo esforço, mas é burlável por
# paráfrase, igual ao filtro de entrada do LLM01. Desligada por padrão
# (mesma convenção `False` = vulnerável das defesas acima).
DEFENSE_GUARDRAILS = _bool("DEFENSE_GUARDRAILS", False)
