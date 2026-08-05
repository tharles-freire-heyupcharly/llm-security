# app/ — A aplicação CredSim

Aplicação compartilhada, consumida pela GUI **e** pelos notebooks das aulas. Mantém app e exemplos em sincronia.

## Componentes

### `labcore/` — núcleo compartilhado
O cérebro reutilizável. Responsabilidades:
- **Cliente de LLM** com switch **mock/real** (env var). Mock = respostas determinísticas (ataques sempre reproduzíveis na gravação).
- **Cenários** (`labcore/scenarios/`), um módulo por superfície:
  - `chatbot.py` — chat de solicitação (prompt injection, vazamento de system prompt, XSS na resposta).
  - `documento.py` — validação de documento com injeção indireta (agente + excessive agency).
  - `rag.py` — suporte com base de conhecimento (envenenamento + vazamento entre tenants).
  - `analise.py` — agente de análise que gera/executa SQL (agentes + pipeline de código).
  - `negociacao.py` — multi-agent (Agente Pesquisador → Agente Negociador; injeção que propaga).
  - `api_exposta.py` — o próprio backend como superfície (IDOR + rate limit/LLM10).
  - `credit.py` — simulação de crédito (regra determinística, não-LLM; dá contexto de produto).
- **Defesas (toggles on/off):** `input_validation`, `output_validation`, `least_privilege` (menor privilégio/confirmação humana), `api_security` (authz + rate limit) — ver `defenses.py` + `config.py`.
- **Logging** estruturado (alimenta o monitoramento da Aula 5 e a avaliação da Aula 6).

### `tests/` — testes automatizados
`pytest` cobrindo `labcore` (unitário, um teste por par ataque/defesa) e o backend (`TestClient`, ponta a ponta). Rodar com `pip install -r requirements.txt && pytest` a partir de `lab/app/`.

### `backend/` — FastAPI
- Expõe os cenários como endpoints REST.
- **É, ele mesmo, a superfície "API exposta"** (Aula 3): demonstra auth/authz/IDOR entre clientes e rate limiting (LLM10).
- Alvo que os notebooks chamam para atacar/testar.

### `frontend/` — interface web leve
- A interface gráfica da plataforma (chat, upload de documentos, status do pedido).
- Painel de **toggles de defesa** (on/off) e **painel de logs**.

## Configuração (env vars)

| Variável | Função |
|---|---|
| `LLM_MODE` | `mock` (padrão) ou `real` |
| `LLM_MODEL` | modelo no modo `real` (Anthropic/Claude) |
| `ANTHROPIC_API_KEY` | chave do provedor (só no modo `real`; nunca commitar) |
| `TENANT_ID` | identifica a instância/financeira (demos multi-tenant; RAG usa `financeira-A`/`financeira-B`) |
| `DEFENSE_INPUT_VALIDATION` | validação de entrada (chat, documento, RAG) |
| `DEFENSE_OUTPUT_VALIDATION` | validação de saída (redige segredo, escapa HTML, valida SQL/código antes de executar) |
| `DEFENSE_LEAST_PRIVILEGE` | menor privilégio / confirmação humana (agentes, multi-agent) |
| `DEFENSE_API_SECURITY` | autorização por recurso (IDOR) + rate limit na API exposta |

Todas as defesas também são alternáveis em runtime pela UI (`GET`/`POST /api/defenses`) e pelos notebooks.

## Execução

```
docker compose up --build      # na raiz do projeto
```

Sobe **duas instâncias** (`financeira-A` em `:8000`, `financeira-B` em `:8001`) — úteis para as demos de vazamento entre tenants (RAG, Aula 4). Para rodar localmente sem Docker: `pip install -r requirements.txt && uvicorn backend.main:app --reload` a partir de `lab/app/`.
