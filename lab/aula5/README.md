# Aula 5 — Mitigações e controles (prática)

**Objetivo:** ligar, uma a uma, as camadas de **defesa em profundidade** e ver os ataques das aulas anteriores serem contidos. É aqui que os **toggles on/off** ganham protagonismo.

## As 5 camadas (cada uma é um toggle na CredSim)

1. **Input validation** — separação de confiança (marcar conteúdo do usuário/documento como dado), limites, classificador de injeção. *(mitiga LLM01 parcial, LLM08)*
2. **Output validation** — schema, encoding antes de renderizar, **filtro de egress/PII**, validar o SQL/Python antes de executar. *(LLM05, LLM02, LLM09)*
3. **Menor privilégio** — ferramentas read-only; **confirmação humana** para e-mail/transferência; escopo apertado. *(LLM06; contém LLM01)*
4. **Guardrails** — política de entrada/saída (tópicos proibidos, vazamento). *(transversal)*
5. **Monitoramento** — logs, detecção de anomalias (custo, chamadas de ferramenta), red-teaming. *(LLM10 + detecção)*

## O que o aluno faz

- Pega um ataque que funcionou na Aula 3/4, **liga a defesa correspondente** e confirma o bloqueio.
- Compara o log com a defesa OFF vs ON.
- Discute por que **nenhuma camada sozinha** basta (defesa em profundidade).

## Arquivos

- `defesas.ipynb` — antes/depois de cada toggle, por ataque.

> A app expõe as defesas como flags (`DEFENSES_*`) controláveis pela UI e pelos notebooks.
