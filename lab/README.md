# Lab — CredSim (laboratório prático do curso LLM Security)

> **CredSim** (nome provisório) é uma **plataforma fictícia de originação de empréstimos com IA**, propositalmente vulnerável, usada para demonstrar **na prática** o conteúdo das 6 aulas do curso. Para cada aula há uma pasta com a exemplificação prática correspondente.
>
> ⚠️ **Uso educacional.** Tudo roda em ambiente fictício/sandbox, com dados sintéticos. Ferramentas "perigosas" (e-mail, transferência, APIs de fornecedores) são **simuladas**. Não use estas técnicas contra sistemas de terceiros.

## O que é

O cliente pede um empréstimo via chat; a plataforma cadastra os dados, analisa risco com agentes, valida documentos, integra fornecedores de crédito e notifica por e-mail. Cada funcionalidade encarna uma **superfície de ataque** e um conjunto de **riscos OWASP Top 10 for LLMs (2025)**.

A graça pedagógica: cada cenário tem um **toggle on/off** (vulnerável ↔ mitigado). O aluno **ataca**, vê passar; **liga a defesa**, vê bloquear; **observa** nos logs.

## Arquitetura

```
lab/
├── app/                     # a aplicação compartilhada
│   ├── labcore/             # núcleo: cliente LLM (mock/real), cenários, defesas (toggles), logging
│   ├── backend/             # FastAPI — também É a superfície "API exposta"
│   ├── frontend/            # interface web leve da plataforma
│   └── tests/               # pytest — cenário negativo/positivo de cada superfície
├── aula1/ … aula6/          # exemplificação prática por aula (guia + notebooks + scripts)
└── README.md                # este arquivo
```

- **Motor de LLM:** `mock` (determinístico, padrão para gravação) **ou** `real` (API/local), via **switch por variável de ambiente**.
- **Notebooks Jupyter:** em paralelo à app, consomem o `labcore`/a API para atacar, alternar defesas e testar/corrigir.
- **Docker:** roda como app web; **múltiplas instâncias = múltiplos "tenants/financeiras"** (para demos de vazamento entre tenants). Parâmetros via env vars.

## Mapa: funcionalidade → superfície → OWASP 2025

| Funcionalidade CredSim | Superfície | OWASP 2025 |
|---|---|---|
| Chat de solicitação | Chatbot | LLM01, LLM07, LLM02 |
| Suporte com documentação | RAG | LLM08, LLM01, LLM02 |
| Análise (gera/executa SQL/Python) | Agentes + Pipeline de código | LLM06, LLM05 |
| Validação de documentos enviados | Agente + injeção indireta | LLM01, LLM06 |
| Perfil/risco → negociação com fornecedor | Multi-agent | LLM06, LLM01 |
| Notificações por e-mail | Agente (ação) | LLM06 |
| Integração c/ fornecedores de crédito | Egress/tools | Aula 4, LLM03 |
| API REST do backend | API exposta | LLM10, LLM02 |

## Índice por aula

| Aula | Tema | Pasta |
|---|---|---|
| 1 | Como LLMs funcionam (fundamentos) | [aula1/](aula1/) |
| 2 | OWASP Top 10 para LLMs (2025) | [aula2/](aula2/) |
| 3 | Superfícies de ataque | [aula3/](aula3/) |
| 4 | Dados e privacidade (LGPD) | [aula4/](aula4/) |
| 5 | Mitigações e controles | [aula5/](aula5/) |
| 6 | Avaliação de segurança (capstone) | [aula6/](aula6/) |

## Status

✅ **App completo.** As 6 superfícies estão implementadas em `app/labcore/scenarios/`: chatbot (+ XSS), RAG, agente de análise (pipeline de código), multi-agent (negociação) e API exposta (IDOR + rate limit) — cada uma com seu par ataque/defesa e coberta por testes automatizados (`app/tests/`, `pytest`). Decisões do projeto em `../PROJECT_CONTEXT.md`.
