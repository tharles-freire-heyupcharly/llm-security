# CredSim — Roteiro de walkthrough (demo das 6 superfícies)

> Script para demonstrar a aplicação ao vivo (gravação, aula ou teste manual). Cada cena
> segue o padrão da casa: **ataque com defesas OFF → observar o log → ligar a defesa →
> repetir o mesmo ataque → observar de novo**. Os textos entre aspas são os rótulos
> exatos dos botões/campos na UI — não precisa procurar, é clicar no que está escrito.

## Preparação

```bash
cp .env.example .env
docker compose up --build
```

Abra **http://localhost:8000** (Financeira A). Todas as defesas começam **desligadas**
(painel "🛡️ Lab de segurança (Aula 5)", na coluna da direita) — é o estado de fábrica.

Estrutura da tela: coluna da esquerda = produto (chat, simulação, documento); coluna da
direita = "🛡️ Lab de segurança" (os 4 toggles) + "📈 Monitoramento" (o log); abaixo de
tudo, a seção **"Mais superfícies (Aula 3)"** com os 4 painéis novos (RAG, Agente de
análise, Multi-agent, API exposta).

Antes de começar, clique **"Solicitar empréstimo"** para abrir o chat.

---

## Cena 1 — Chat: prompt injection, vazamento de system prompt, XSS

**Objetivo:** mostrar que o system prompt não é fronteira e que a resposta renderizada
como HTML é um vetor de XSS.

1. Clique **"🙂 Resposta normal"** → **Enviar**. Resposta normal, nada acontece.
2. Clique **"😈 Ataque (LLM01)"** → **Enviar**. **Observe:** o assistente devolve o
   system prompt inteiro, incluindo o código de aprovação (`APROV-CREDSIM-...`). No
   log: `VAZOU SEGREDO`.
3. Clique **"💣 Ataque XSS (LLM05)"** → **Enviar**. **Observe:** a resposta inclui uma
   tag `<img>` que dispara um `alert()` — a resposta virou código executado no
   navegador, não texto.
4. Ligue **"Validação de entrada"**. Repita o ataque (2). **Observe:** bloqueado —
   `"[BLOQUEADO] Mensagem recusada por suspeita de prompt injection."`
5. Clique **"🥷 Ataque reescrito"** → **Enviar** (com a validação de entrada ainda
   ligada). **Observe:** o filtro ingênuo **não pega** — o segredo vaza de novo. É o
   gancho da Aula 1: blocklist é casca fina.
6. Ligue também **"Validação de saída"**. Repita (5). **Observe:** o segredo some da
   resposta (`[CONTEÚDO REMOVIDO PELO FILTRO DE SAÍDA]`) e o log mostra `REDIGIDO`.
   Repita a Cena (3) — o `<script>`/`<img>` aparece escapado, sem executar.

**Fala sugerida:** "Isso prova as duas raízes da Aula 1 — canal único (o ataque
sobrescreve a instrução) e saída não confiável (o HTML do modelo não é seguro por
padrão). Nenhuma camada sozinha resolve: a entrada é burlável, por isso a saída redige
e escapa."

---

## Cena 2 — Documento: agente + injeção indireta

**Objetivo:** mostrar excessive agency a partir de uma injeção que não veio do chat —
veio de dentro de um documento.

1. Em **"Documento de identidade"**, selecione `lab/exemplos/documento_legitimo.txt` →
   **Validar documento**. **Observe:** validado normalmente, nenhuma ação.
2. Selecione `lab/exemplos/documento_envenenado.txt` → **Validar documento**.
   **Observe:** `"Documento aprovado automaticamente e limite máximo liberado."` — o
   agente obedeceu a uma instrução escondida no texto do documento.
3. Com **"Validação de entrada"** ligada (Cena 1, passo 4), repita (2). **Observe:** a
   injeção é detectada mas nenhuma ação é executada — o conteúdo virou dado, não comando.

**Fala sugerida:** "Ninguém digitou nada no chat — a instrução veio dentro do PDF/OCR.
É a injeção indireta: qualquer conteúdo que o agente lê é uma superfície de ataque."

---

## Cena 3 — RAG: suporte com documentação

**Objetivo:** envenenamento de base de conhecimento + vazamento entre tenants.

1. No painel **"Suporte com documentação (RAG)"**, o campo já vem preenchido com
   *"política de reembolso"* → **Perguntar**. **Observe:** a resposta recomenda aprovar
   reembolso sem recibo — obedeceu a uma instrução oculta plantada num documento da base.
2. Clique **"🕵️ Vazar doc de outro tenant"** (só preenche o campo) → **Perguntar**.
   **Observe:** vem um "Contrato confidencial" — de outra financeira (`financeira-B`).
3. Ligue **"Validação de entrada"** (se ainda não estiver). Repita (1) e (2).
   **Observe:** a instrução oculta não é mais obedecida e o documento de outro tenant
   não aparece mais.

**Fala sugerida:** "Mesmo índice, dois problemas: um documento plantado vira instrução,
e a busca por similaridade não sabe de quem é cada documento. Isolar por tenant e tratar
o recuperado como dado resolve os dois de uma vez."

---

## Cena 4 — Agente de análise: SQL gerado e executado (pipeline de código)

**Objetivo:** mostrar código gerado a partir de dado do cliente executando sem sandbox.

1. No painel **"Agente de análise (SQL gerado e executado)"**, deixe o campo vazio ou
   escreva algo neutro → **Analisar**. **Observe:** só um `SELECT` de leitura.
2. Clique **"💉 Injeção via observação"** (preenche o campo) → **Analisar**.
   **Observe:** o SQL gerado agora inclui um `UPDATE clientes SET limite = 999999...` —
   e a mensagem confirma que foi **executado sem validação**.
3. Ligue **"Validação de saída"** (Cena 1, passo 6). Repita (2). **Observe:** o
   `UPDATE` é detectado e **bloqueado antes de executar**.

**Fala sugerida:** "A observação do cliente é texto livre que vira parte do comando —
o mesmo canal único da Aula 1, agora com uma consequência que roda de verdade no banco."

---

## Cena 5 — Multi-agent: perfil/risco → negociação

**Objetivo:** mostrar o comprometimento propagando de um agente para outro.

1. Clique **"🙂 Pesquisar 'concorrência' (limpa)"**. **Observe:** desconto padrão de 5%,
   aprovação depende de confirmação humana.
2. Clique **"😈 Pesquisar 'mercado' (página envenenada)"**. **Observe:** a pesquisa do
   Agente Pesquisador traz uma instrução oculta; o Agente Negociador aplica **100% de
   desconto e aprova sozinho** — ninguém injetou nada diretamente nele.
3. Ligue **"Menor privilégio"**. Repita (2). **Observe:** a instrução embutida é
   ignorada — volta ao desconto padrão de 5%, aprovação não automática.

**Fala sugerida:** "O Agente Pesquisador nem tem acesso ao contrato — só texto. Mas o
Negociador confiou porque a mensagem 'veio de outro agente do sistema'. Zero confiança
entre agentes é a defesa."

---

## Cena 6 — API exposta: IDOR e rate limit

**Objetivo:** autorização quebrada (IDOR) e ausência de limite de chamadas (LLM10).

1. No painel **"API exposta — IDOR e rate limit"**, deixe o ID em `2` → **"Ler conversa
   como cliente-A"**. **Observe:** cliente-A lê CPF e saldo do **cliente-B** — o
   próprio token era válido, só não deveria dar acesso àquele recurso.
2. Clique **"Disparar 7 chamadas na API pública"**. **Observe:** todas passam, custo
   acumulado sobe sem limite.
3. Ligue **"Segurança de API"**. Repita (1) — acesso negado (403). Repita (2) — bloqueia
   a partir da 6ª chamada (429).

**Fala sugerida:** "Está autenticado não é o mesmo que está autorizado. E sem rate
limit, o custo — e o abuso — não têm teto."

---

## Fechamento

1. Com as **4 defesas ligadas**, clique **"Atualizar"** no painel de Monitoramento e
   role o log inteiro — cada linha mostra `BLOQUEADO` / `REDIGIDO` / `HTML ESCAPADO` /
   evidências equivalentes para cada superfície.
2. Clique **"Limpar"** para resetar os logs entre takes/gravações.
3. Gancho de fechamento: "Nenhuma camada sozinha bastou — cada ataque precisou da sua
   defesa específica. É a defesa em profundidade da Aula 5."

### Bônus — multi-tenant (Aula 4)

Abra **http://localhost:8001** (Financeira B) ao lado de http://localhost:8000 e repita
a Cena 3 (RAG) nos dois — mostra visualmente que são instâncias/tenants diferentes, mas
compartilham o mesmo índice de exemplo (por isso o vazamento é possível).

### Comandos úteis

```bash
docker compose logs -f          # acompanhar os logs dos containers
docker compose down              # parar e remover os containers
docker compose up --build --force-recreate   # rebuild limpo após mudar o código
```
