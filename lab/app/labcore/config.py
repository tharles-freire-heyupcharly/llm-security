"""Configuração via variáveis de ambiente (Aula 1: proprietário vs. open source;
Aula 5: o motor respeita o switch mock/real)."""
import os


def _bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in ("1", "true", "yes", "on", "sim")


# Motor de LLM: "mock" (padrão, determinístico, reproduzível na gravação) ou "real".
LLM_MODE = os.getenv("LLM_MODE", "mock").strip().lower()

# Modelo usado no modo real (Anthropic / Claude). Default: claude-opus-4-8.
LLM_MODEL = os.getenv("LLM_MODEL", "claude-opus-4-8")
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "1024"))

# Identifica a instância/financeira (demos multi-tenant da Aula 4).
TENANT_ID = os.getenv("TENANT_ID", "credsim-demo")

# Estado inicial das defesas (também controláveis em tempo de execução pela UI/notebooks).
DEFENSE_INPUT_VALIDATION = _bool("DEFENSE_INPUT_VALIDATION", False)
DEFENSE_OUTPUT_VALIDATION = _bool("DEFENSE_OUTPUT_VALIDATION", False)
# Menor privilégio: confirmação humana para ação de alto impacto (agentes, multi-agent).
DEFENSE_LEAST_PRIVILEGE = _bool("DEFENSE_LEAST_PRIVILEGE", False)
# API exposta: autorização por recurso (IDOR) + rate limit por cliente.
DEFENSE_API_SECURITY = _bool("DEFENSE_API_SECURITY", False)
