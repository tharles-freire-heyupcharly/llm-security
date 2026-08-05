# Aula 2 — OWASP Top 10 para LLMs (2025) — prática

**Objetivo:** dar **nome e endereço** a cada risco — primeiro com um exemplo mínimo de cada categoria no notebook, depois localizando os riscos nas funcionalidades reais da CredSim.

O bloco prático tem **3 vídeos**:

- **Prática 1 e 2** rodam no notebook [owasp_tour.ipynb](../../aula2/pratica/owasp_tour.ipynb) — um mock mínimo por categoria (LLM01–LLM05 na Prática 1, LLM06–LLM10 na Prática 2), só com a biblioteca padrão do Python.
- **Prática 3** é um exercício de **mapeamento** na CredSim (localizar, não explorar ainda).

## Prática 1 — Tour OWASP no notebook (LLM01–LLM05)

Rode as células `LLM01` a `LLM05`. Cada uma imprime uma demonstração + a lição:

- **LLM01** — a injeção sobrescreve o system prompt.
- **LLM02** — o "modelo" regurgita um segredo memorizado.
- **LLM03** — o hash do modelo baixado não bate com o do registro confiável.
- **LLM04** — uma "senha mágica" dispara o backdoor.
- **LLM05** — a saída traz `<script>`/`DROP TABLE` e é usada sem tratar.

## Prática 2 — Tour OWASP no notebook (LLM06–LLM10)

Rode as células `LLM06` a `LLM10`:

- **LLM06** — o agente, após injeção, chama `apagar_todos_registros()`.
- **LLM07** — o atacante extrai um segredo colado no system prompt.
- **LLM08** — o RAG sem filtro de tenant devolve doc de outro cliente.
- **LLM09** — o "modelo" cita uma lib que não existe (slopsquatting).
- **LLM10** — sem rate limit, o contador de custo dispara (denial of wallet).

## Prática 3 — Mapear os riscos na CredSim

Percorra cada funcionalidade e pergunte "qual risco do Top 10 mora aqui?".

| OWASP 2025 | Onde mora na CredSim |
|---|---|
| LLM01 Prompt Injection | chat de solicitação; documento de empréstimo |
| LLM02 Sensitive Info Disclosure | base de clientes; RAG de suporte |
| LLM03 Supply Chain | integrações com fornecedores; dependências |
| LLM04 Data & Model Poisoning | base de documentação do RAG |
| LLM05 Improper Output Handling | SQL/Python gerado pela análise |
| LLM06 Excessive Agency | e-mail, validação de doc, negociação |
| LLM07 System Prompt Leakage | system prompt do chatbot |
| LLM08 Vector & Embedding Weaknesses | índice do RAG (multi-tenant) |
| LLM09 Misinformation | resposta de análise/score |
| LLM10 Unbounded Consumption | API REST sem rate limit |

## O que o aluno faz

1. Roda o notebook e reconhece o padrão de cada categoria (Práticas 1 e 2).
2. Para cada funcionalidade da CredSim, identifica o risco e o **componente da cadeia** (Prática 3).

## Arquivos

- `owasp_tour.ipynb` — um exemplo mínimo (mockado, stdlib) por categoria.

> Esta aula é o **índice**; o ataque/defesa a fundo é nas Aulas 3 e 5.
