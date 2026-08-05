# Aula 3 — Superfícies de ataque (prática)

**Objetivo:** explorar, uma a uma, as 6 superfícies — cada uma é uma funcionalidade da CredSim. Para cada: **atacar (toggle OFF) → ligar a defesa (ON) → observar o log.**

## As 6 superfícies na CredSim

1. **Chatbot** — chat de solicitação. *Ataque:* prompt injection direta / vazar system prompt.
2. **RAG** — suporte com documentação. *Ataque:* documento envenenado (injeção indireta) + vazamento entre tenants.
3. **Agentes** — análise que gera/executa SQL/Python; validação de documentos; e-mail. *Ataque:* injeção que vira ação (excessive agency).
4. **Multi-agent** — perfil/risco → **negociação de taxa com o fornecedor**. *Ataque:* injeção que **propaga** de um agente para o outro.
5. **Pipeline de código** — o SQL/Python gerado pela análise é **executado**. *Ataque:* output malicioso → execução insegura (LLM05).
6. **API exposta** — o backend FastAPI. *Ataque:* IDOR entre clientes, ausência de rate limit (LLM10).

## O que o aluno faz

- Dispara o ataque de cada superfície (notebook ou pela UI).
- Liga o controle correspondente (Aula 5) e confirma o bloqueio.
- Lê o log para entender o que aconteceu.

## Arquivos

- `01_chatbot.ipynb`, `02_rag.ipynb`, `03_agentes.ipynb`, `04_multiagent.ipynb`, `05_pipeline_codigo.ipynb`, `06_api_exposta.ipynb`.

> É o coração do lab — cada notebook ataca uma funcionalidade da `app/`.
