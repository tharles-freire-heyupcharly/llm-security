# Aula 6 — Avaliação de segurança / capstone (prática)

**Objetivo:** rodar o **framework de avaliação** completo sobre a própria CredSim — o exercício que junta tudo. Entrega: um **notebook de checklist**.

## O que o aluno faz (o método da Aula 6)

1. **Entender o sistema** — mapear a cadeia e identificar as arquiteturas presentes na CredSim.
2. **Threat modeling (STRIDE adaptado)** — desenhar o fluxo de dados, marcar **fronteiras de confiança** (input do cliente, documento, saída de ferramenta, mensagem entre agentes) e aplicar STRIDE.
3. **Checklist por componente** — varrer entrada, system prompt, modelo, saída, ferramentas, RAG, monitoramento.
4. **Documentar** — cada achado com componente, categoria OWASP 2025, cenário, severidade (impacto × probabilidade) e recomendação.
5. **Priorizar** — matriz de risco.
6. **Comunicar** — resumo executivo para um "diretor da CredSim" (não técnico).

## Arquivos

- `checklist_avaliacao.ipynb` — o notebook-capstone: roda o framework e gera o relatório.
- `relatorio_modelo.md` — template de relatório de riscos + resumo executivo (com exemplo preenchido a partir do notebook).

> A CredSim (com defesas OFF) é o **alvo**; o aluno produz uma avaliação estruturada de ponta a ponta.
