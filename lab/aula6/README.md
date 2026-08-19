# Aula 6 — Avaliação de segurança / capstone (prática)

**Objetivo:** rodar o **framework de avaliação** completo sobre a própria CredSim — o exercício que junta tudo. Entrega: um **notebook de checklist**.

> Alvo desta rodada: **`lab/app_v2`** (CredSim v2, porta `8010` —
> `docker compose up --build` na raiz do projeto). O `lab/app` (v1, porta
> `8000`) segue intacto como referência/backup; os arquivos abaixo já foram
> atualizados para o comportamento real do v2 (5 toggles de defesa, motor de
> IA em 3 modos, fluxo de menor privilégio propor→confirmar, identidade
> `admin1`).

## O que o aluno faz (o método da Aula 6)

1. **Entender o sistema** — mapear a cadeia e identificar as arquiteturas presentes na CredSim.
2. **Threat modeling (STRIDE adaptado)** — desenhar o fluxo de dados, marcar **fronteiras de confiança** (input do cliente, documento, saída de ferramenta, mensagem entre agentes) e aplicar STRIDE.
3. **Checklist por componente** — varrer entrada, system prompt, modelo, saída, ferramentas, RAG, monitoramento.
4. **Documentar** — cada achado com componente, categoria OWASP 2025, cenário, severidade (impacto × probabilidade) e recomendação.
5. **Priorizar** — matriz de risco.
6. **Comunicar** — resumo executivo para um "diretor da CredSim" (não técnico).

## Arquivos

- `diagrama_contexto.md` — diagrama de contexto (C1), mapa das 6 superfícies de LLM da Aula 3 aplicadas ao código real do `app_v2`, e mapa de componentes internos com as 9 fronteiras de confiança (STRIDE). É o **gabarito** do Passo 1–2 do método — mostre depois que o aluno tentar desenhar o próprio.
- `checklist_avaliacao.ipynb` — o notebook-capstone: roda o framework e gera o relatório.
- `relatorio_modelo.md` — template de relatório de riscos + resumo executivo (com exemplo preenchido a partir do notebook).
- `avaliacao_stride/` — a mesma avaliação, em **6 páginas HTML navegáveis** (uma por passo do método, mais um índice), cobrindo o conteúdo teórico completo dos 6 vídeos da aula (não só a prática): matriz STRIDE cruzando as 6 letras com os 8 componentes, checklist de entrada/saída/monitoramento, os 16 achados com a anatomia completa (componente, OWASP, cenário, severidade, recomendação), matriz de risco impacto×probabilidade, e um **resumo executivo com layout de relatório para diretor** (postura geral, riscos em linguagem de negócio, próximas ações). 100% local, sem servidor nem internet — abra `avaliacao_stride/00_indice.html` direto no navegador (duplo clique ou `file://`) e navegue pelos links entre as 6 páginas.

> A CredSim (com defesas OFF) é o **alvo**; o aluno produz uma avaliação estruturada de ponta a ponta. Ver também `lab/app_v2/AULA6_ROTEIRO_PRATICO.md` — roteiro de gravação com os comandos `curl` equivalentes a cada célula do notebook.
