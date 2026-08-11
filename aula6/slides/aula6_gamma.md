# Aula 6 — Avaliando a segurança de uma aplicação de LLM

- **Curso LLM Security · Aula 6** — de conhecimento a método: juntamos tudo num processo de avaliação.
- **Avaliar e comunicar** — a habilidade-fim do curso.

<!-- ═══ VÍDEO 1 · Abertura — de conhecimento a método · ~5 min ═══
Objetivo: enquadrar a aula de fechamento (juntar tudo num processo repetível) e prometer o resultado (avaliar + comunicar). Vídeo autocontido: abre e fecha ("a seguir, o método de avaliação em quatro passos").
-->

<!--
LAYOUT: capa — título grande + subtítulo; tema Alura, accent #1F53E5; imagens = None (fundo sóbrio). Nada crítico no canto inferior direito (safe zone da facecam).
ROTEIRO: síntese e chegada — a última aula tem um papel especial: juntar tudo (vocabulário da Aula 1, riscos da Aula 2, arquiteturas da 3, ataques da 4, defesas da 5) num processo de avaliação repetível em qualquer app de LLM. E o diferencial profissional: avaliar não basta, você precisa COMUNICAR para quem decide. Tom animado — chegamos ao fim da trilha.
-->

---

## O que veremos nesta aula
_introdução_

<!--
LAYOUT: agenda com 4 itens, um ícone por item; accent #1F53E5. Sem diagrama.
ROTEIRO: mapa rápido — o método de avaliação (processo de 4 passos: entender → modelar → checar → priorizar), o STRIDE adaptado ao LLM, documentar e comunicar (achados priorizados + resumo executivo) e o laboratório sobre a CredSim. Não passe de ~30s.
-->

- **Método de avaliação** — um processo estruturado e repetível.
- **STRIDE adaptado** — threat modeling: o que pode dar errado, por componente.
- **Documentar e comunicar** — riscos priorizados e resumo executivo para quem decide.
- **Laboratório** — rodar o método inteiro sobre a CredSim.

---

<!-- ═══ VÍDEO 2 · Método de avaliação de segurança · ~10 min ═══  (ementa: framework de avaliação de segurança para aplicações de LLM) -->

## Um método de avaliação de segurança
_conteúdo_

<!--
LAYOUT: diagrama de 4 passos em sequência (entender → modelar → checar → priorizar) nativo no Gamma. Accent #1F53E5.
ROTEIRO: o processo estruturado (na ementa, o "framework de avaliação") — repetível em qualquer app. Passo 1, entender: antes de procurar vulnerabilidade, mapeie a cadeia (Aula 1: modelo → orquestração → ferramentas → dados) e identifique a arquitetura (Aula 3: chat? RAG? agente?). Sem esse mapa você não sabe onde procurar. Passo 2, levantar ameaças: com o mapa, o OWASP Top 10 2025 (Aula 2, documento padrão de conscientização) é o ponto de partida, e o threat modeling sistematiza.
-->

- **Entender o sistema** — mapear a cadeia (Aula 1) e identificar a arquitetura (Aula 3: chat? RAG? agente?).
- **Levantar ameaças** — aplicar o OWASP Top 10 2025 (Aula 2) + threat modeling.

---

## Método de avaliação — checar e priorizar
_conteúdo_

<!--
LAYOUT: 2 bullets; matriz impacto × probabilidade ao lado, nativa no Gamma. Accent #1F53E5.
ROTEIRO: passo 3, avaliar controles: levantar ameaças sem olhar os controles é meio trabalho — cheque as 5 camadas de defesa em profundidade (Aula 5); a pergunta central é 'cada risco levantado tem um controle correspondente?'. Passo 4, priorizar: nem todo risco tem a mesma urgência; a matriz impacto × probabilidade decide a ordem. A lógica do curso: a arquitetura (passo 1) define os riscos mais prováveis; o checklist (passo 3) mostra onde falta controle; a priorização junta os dois.
-->

- **Avaliar controles** — checar as 5 camadas de defesa (Aula 5): a defesa em profundidade está presente?
- **Priorizar** — por impacto × probabilidade; a arquitetura define os riscos, você avalia se os controles cobrem.

---

<!-- NOVO SLIDE (revisar e colar no Gamma) -->
## Método em ação — um mini-exemplo na CredSim
_conteúdo_

<!--
LAYOUT: 4 mini-cards em sequência (um por passo do método), cada um com 1 frase sobre a CredSim; o último com o marcador Segurança:. Accent #1F53E5.
ROTEIRO: cenário concreto e rápido, sobre o componente Suporte (RAG) da CredSim. Passo 1, entender: o Suporte responde perguntas do cliente puxando documentos de um índice vetorial único, compartilhado entre todos os clientes. Passo 2, levantar ameaças: o threat modeling aponta o risco mais provável ali — LLM08, vazamento entre tenants, porque o índice não separa por conta. Passo 3, avaliar controles: ao checar as 5 camadas de defesa (Aula 5), não existe filtro de tenant na busca — controle ausente, confirmado, não é hipótese. Passo 4, o achado já nasce priorizado: impacto alto (dado de cliente vaza) × probabilidade alta (acontece em qualquer busca) = crítico. É o mesmo exercício que o aluno vai fazer sozinho no capstone — aqui o professor guia passo a passo.
-->

- **1. Entender** — o Suporte (RAG) da CredSim responde perguntas puxando documentos de um índice vetorial único, compartilhado entre todos os clientes.
- **2. Levantar ameaças** — o risco mais provável nesse componente é o LLM08 (vazamento entre tenants): o índice não separa por conta.
- **3. Avaliar controles** — ao checar as 5 camadas de defesa (Aula 5), não há filtro de tenant na busca vetorial — controle ausente, confirmado.
- **Segurança: 4. o achado já nasce priorizado** — impacto alto (dado de cliente vaza) × probabilidade alta (ocorre em qualquer busca) = crítico.

---

<!-- ═══ VÍDEO 3 · Threat modeling — STRIDE adaptado · ~11 min ═══  (ementa: threat modeling para IA, adaptando o STRIDE) -->

## Threat modeling — STRIDE adaptado ao LLM
_conteúdo_

<!--
LAYOUT: tabela nativa no Gamma ligando cada letra do STRIDE ao(s) risco(s) OWASP 2025. Accent #1F53E5.
ROTEIRO: STRIDE é um acrônimo da Microsoft (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege) — um checklist mental de ameaças, não ferramenta nova, e funciona bem adaptado ao LLM. Ligue cada letra ao OWASP 2025: Tampering → LLM04 (envenenar modelo) e LLM08 (envenenar RAG); Information Disclosure → LLM02 (vazar dados) e LLM07 (system prompt); DoS → LLM10 (consumo ilimitado); Elevation → LLM06 (agência/ferramentas). Spoofing e Repudiation são transversais (autenticação e logs), baixa aderência específica ao LLM.
-->

- **STRIDE → LLM** — Tampering → LLM04/LLM08, Disclosure → LLM02/LLM07, DoS → LLM10, Elevation → LLM06.
- **Spoofing e Repudiation** — transversais (autenticação e logs); baixa aderência específica ao LLM.

---

## Threat modeling — fronteiras de confiança
_conteúdo_

<!--
LAYOUT: diagrama de fluxo de dados com as fronteiras de confiança marcadas (usuário, doc de RAG, saída de ferramenta, msg de outro agente) nativo no Gamma. Accent #1F53E5.
ROTEIRO: o insight central — a fronteira de confiança. Retome a Aula 1: no LLM a parede entre instrução e dado quase não existe, então TODA entrada não-confiável é uma fronteira a mapear: o texto do usuário, um doc indexado no RAG, a resposta de uma ferramenta, a mensagem de outro agente. Operacionalize: desenhe o fluxo de dados (quem envia o quê para quem), marque cada fronteira e, em cada uma, pergunte 'qual letra do STRIDE pode se materializar aqui?'. É o exercício central do laboratório.
-->

- **Segurança: fronteiras de confiança** — como a parede instrução×dado é borrada, toda entrada não-confiável é uma fronteira (usuário, RAG, ferramenta, outro agente).
- **Fluxo de dados** — desenhe o fluxo, marque as fronteiras e aplique STRIDE em cada uma.

---

<!-- NOVO SLIDE (revisar e colar no Gamma) -->
## STRIDE em ação — a fronteira que ninguém tinha marcado
_conteúdo_

<!--
LAYOUT: antes/depois do diagrama de fluxo de dados da CredSim — a fronteira "documento indexado" ausente, depois marcada; o último bullet com o marcador Segurança:. Accent #1F53E5.
ROTEIRO: cenário concreto. No primeiro diagrama que o time desenhou da CredSim, o fluxo ia usuário → modelo → resposta; o documento indexado no RAG entrou como "dado interno", sem virar uma fronteira de confiança marcada — parecia inofensivo por estar "dentro de casa". Ao revisar com o STRIDE, alguém pergunta: essa fronteira permite Tampering? A resposta é sim — um documento malicioso indexado altera a resposta para todo cliente que recuperar aquele trecho (LLM04/LLM08). A fronteira esquecida vira achado formal: falta validação de conteúdo antes de indexar. Lição que fecha o vídeo: qualquer fronteira "que parece interna" ainda é fronteira.
-->

- **O diagrama original** — o fluxo desenhado pelo time ia usuário → modelo → resposta; o documento indexado no RAG entrou como "dado interno", sem virar fronteira marcada.
- **A pergunta do STRIDE** — na revisão, alguém pergunta: essa fronteira permite Tampering? Sim — um documento malicioso indexado altera a resposta para todo cliente que recuperar aquele trecho (LLM04/LLM08).
- **O achado** — a fronteira esquecida vira item formal do relatório: falta validação de conteúdo antes de indexar.
- **Segurança: toda fronteira conta, mesmo a que "parece interna"** — dado indexado também é entrada não-confiável.

---

<!-- ═══ VÍDEO 4 · Revisão de arquitetura — checklist por componente · ~11 min ═══  (ementa: revisão de arquitetura de segurança, checklist por componente) -->

## Checklist por componente — entrada e saída
_conteúdo_

<!--
LAYOUT: 2 blocos (entrada/modelo × saída/ferramentas/RAG), cada pergunta com o risco ao lado, nativo no Gamma. Accent #1F53E5.
ROTEIRO: percorra os componentes da cadeia fazendo as perguntas certas. Entrada/modelo: há authz e rate limit (LLM01/LLM10)? o system prompt guarda segredo ou a segurança depende de ele ser secreto (LLM07)? a proveniência do modelo foi verificada (LLM03)? Saída/execução: a saída é tratada como não-confiável e sanitizada antes de renderizar/executar (LLM05)? as ferramentas têm menor privilégio e human-in-the-loop (LLM06)? há isolamento de tenant no RAG (LLM08)? Para cada 'não', mencione rápido o que acontece — torna o checklist concreto.
-->

- **Entrada, system prompt, modelo** — há authz e rate limit (LLM01/LLM10)? segredo no system prompt (LLM07)? proveniência do modelo verificada (LLM03)?
- **Saída, ferramentas, RAG** — a saída é sanitizada (LLM05)? ferramentas com menor privilégio + human-in-the-loop (LLM06)? isolamento de tenant no RAG (LLM08)?

---

## Checklist por componente — a matriz que amarra o curso
_conteúdo_

<!--
LAYOUT: 2 bullets; tabela componente × risco × controle nativa no Gamma, com uma célula vazia destacada (o gap). Accent #1F53E5.
ROTEIRO: monitoramento — uma app segura no deploy não garante segurança em produção: há logs para investigar um incidente? detecção de anomalias (volume, padrões de injeção, respostas fora do perfil)? red-teaming periódico? (LLM10 + detecção geral). E o insight estrutural que amarra o curso: cada linha do checklist cruza os três eixos — um componente (Aula 1), um risco do OWASP 2025 (Aula 2) e um controle de defesa em profundidade (Aula 5). Uma célula de controle vazia é um gap. Pausa depois desta síntese.
-->

- **Monitoramento** — há logs? detecção de anomalias? red-teaming periódico (LLM10 + detecção geral)?
- **Segurança: componente × risco × controle** — cada linha cruza os três eixos (Aulas 1, 2 e 5); célula vazia = gap.

---

<!-- NOVO SLIDE (revisar e colar no Gamma) -->
## Checklist em ação — a célula vazia que virou achado
_conteúdo_

<!--
LAYOUT: uma linha da matriz componente × risco × controle em destaque (API / LLM10 / rate limit), célula de controle vazia marcada; o último bullet com o marcador Segurança:. Accent #1F53E5.
ROTEIRO: cenário concreto no componente API da CredSim. A pergunta do checklist: há rate limit e quota por usuário? A resposta, ao inspecionar a configuração: não — qualquer chave de API autenticada pode disparar milhares de chamadas sem limite algum. Na matriz componente × risco × controle, a linha "API / LLM10 / rate limit" fica com a célula de controle vazia — um gap real, encontrado, não hipotético. Reforce: célula vazia não é só observação; vira achado com severidade e recomendação no mesmo instante.
-->

- **A pergunta** — no componente API da CredSim: há rate limit e quota por usuário?
- **A resposta** — não; qualquer chave de API autenticada pode disparar milhares de chamadas sem limite.
- **A célula vazia** — na matriz componente × risco × controle, a linha "API / LLM10 / rate limit" fica sem controle — um gap real, não hipotético.
- **Segurança: célula vazia vira achado na hora** — não é só uma observação; já entra no relatório com severidade e recomendação.

---

<!-- ═══ VÍDEO 5 · Documentar riscos e recomendações · ~10 min ═══  (ementa: documentando riscos e recomendações) -->

## Documentar — a anatomia de um achado
_conteúdo_

<!--
LAYOUT: card de um achado com os 6 campos; ao lado, matriz de risco 3×3 nativa no Gamma. Accent #1F53E5.
ROTEIRO: encontrar o risco é metade do trabalho — documentar bem é o que torna a avaliação útil. Cada achado tem estrutura mínima: descrição, componente afetado, categoria OWASP 2025, cenário de exploração (concreto, não abstrato — é o campo que convence), severidade e recomendação. Com vários achados, priorize: a matriz impacto × probabilidade decide a ordem (alto×alto = crítico; alto×baixo = monitorar; baixo×alto = backlog). Uma tabela 3×3 simples já comunica prioridade.
-->

- **Cada achado** — descrição + componente + categoria OWASP + cenário de exploração + severidade + recomendação.
- **Priorizar** — uma matriz de risco (impacto × probabilidade) decide a ordem.

---

<!-- NOVO SLIDE (revisar e colar no Gamma) -->
## Documentar — um achado completo, campo a campo
_conteúdo_

<!--
LAYOUT: card do achado preenchido nos 6 campos, um por linha; o último bullet com o marcador Segurança:. Accent #1F53E5.
ROTEIRO: instancie a estrutura do slide anterior com um achado real da CredSim. Descrição + componente: o agente de suporte aciona a ferramenta de envio de e-mail sem nenhuma confirmação humana (componente: ferramentas/agente). Categoria + cenário: LLM06 (Excessive Agency); uma injeção escondida no ticket faz o agente enviar automaticamente um e-mail com dados do cliente para um endereço externo. Severidade + recomendação: alta (impacto alto × probabilidade média); exigir confirmação humana explícita antes de qualquer envio. Reforce: é o cenário de exploração que convence um leitor cético — sem ele, o achado parece teórico. Este achado volta no próximo slide para a lição de recomendação acionável.
-->

- **Descrição + componente** — o agente de suporte da CredSim aciona a ferramenta de envio de e-mail sem nenhuma confirmação humana; componente: ferramentas/agente.
- **Categoria + cenário de exploração** — LLM06 (Excessive Agency): uma injeção escondida no ticket faz o agente enviar automaticamente um e-mail com dados do cliente para um endereço externo.
- **Severidade + recomendação** — alta (impacto alto × probabilidade média); recomendação: exigir confirmação humana explícita antes de qualquer envio.
- **Segurança: o cenário é o que convence** — sem ele o achado parece teórico; com ele, qualquer leitor entende o risco real.

---

## Documentar — recomendação acionável
_conteúdo_

<!--
LAYOUT: 2 bullets; contraste "ruim × boa" recomendação, nativo no Gamma. Accent #1F53E5.
ROTEIRO: leia os dois exemplos com entonação contrastante. Ruim (vago): 'seja mais seguro'. Boa (firme e específica): 'adicione confirmação humana na ferramenta de envio de e-mail (LLM06), pois hoje o agente a aciona sozinho'. Três atributos de uma boa recomendação: específica (qual componente, qual mudança), ligada ao risco (referencia o LLM0X e o cenário) e acionável (quem faz o quê). 'Uma recomendação acionável é a que um dev pega amanhã e implementa sem te ligar de volta.'
-->

- **Segurança: recomendação acionável** — específica, ligada ao risco e acionável (ex.: "adicione confirmação humana no envio de e-mail — LLM06").
- **Ruim × boa** — "seja mais seguro" não serve; diga qual componente, qual mudança e quem faz.

---

<!-- ═══ VÍDEO 6 · Apresentar riscos a stakeholders não técnicos · ~9 min ═══  (ementa: como apresentar riscos de LLM para stakeholders não técnicos) -->

## Apresentar a quem decide — linguagem de negócio
_conteúdo_

<!--
LAYOUT: 2 bullets; tradução "sigla técnica → consequência de negócio", nativa no Gamma. Accent #1F53E5.
ROTEIRO: ponto de ênfase — o erro mais comum do técnico é entregar um relatório cheio de siglas que o tomador de decisão não entende, e então nada é corrigido. Traduzir para negócio não é simplificar, é respeitar o interlocutor: perda financeira, vazamento de dados de cliente, multa de LGPD, dano reputacional. Ex.: 'LLM07 exposto' não diz nada a um diretor; diga 'um atacante extrai as instruções do sistema em 30 segundos, o roteiro completo para contornar os filtros'. Sem FUD — não exagere nem venda medo; seja preciso sobre o impacto real.
-->

- **Segurança: traduza para o negócio** — perda financeira, vazamento de dados de cliente, multa de LGPD, dano reputacional.
- **Sem FUD** — não venda medo; seja preciso ("LLM07 exposto" → "extraem o roteiro para burlar os filtros").

---

## Apresentar a quem decide — o resumo executivo
_conteúdo_

<!--
LAYOUT: 2 bullets; modelo de resumo executivo de 1 página, nativo no Gamma. Accent #1F53E5.
ROTEIRO: o resumo executivo é para o diretor de produto, o CTO ou o cliente — quem não vai ler o relatório técnico. No máximo uma página: qual a postura geral de segurança, quais os 2–3 riscos mais críticos em linguagem de negócio, quais as próximas ações. 'Se você escreve esse resumo com clareza, está pronto para atuar profissionalmente em LLM Security.' Tom motivador — é o pré-fechamento do curso.
-->

- **Uma página** — postura geral + os 2–3 riscos mais críticos (em negócio) + próximas ações.
- **A habilidade decisiva** — clareza + priorização + linguagem de negócio é o que faz o risco ser corrigido.

---

<!-- NOVO SLIDE (revisar e colar no Gamma) -->
## O resumo executivo — um exemplo real (CredSim)
_conteúdo_

<!--
LAYOUT: card de resumo executivo de 1 página preenchido para a CredSim, os 3 blocos (postura, riscos, ações) em destaque; o último bullet com o marcador Segurança:. Accent #1F53E5.
ROTEIRO: instancie o modelo do slide anterior com o resumo real que antecipa o fecho do capstone. Postura geral: "a CredSim apresenta postura de segurança moderada: os principais riscos estão mapeados, mas dois exigem correção antes do lançamento." Os 2 riscos mais críticos, em negócio: dados de um cliente podem aparecer na resposta de outro (risco de vazamento e multa de LGPD); o assistente pode enviar e-mails automaticamente sem revisão humana (risco de erro irreversível). Próximas ações: isolar a busca por conta em até 2 semanas; exigir confirmação humana no envio de e-mail antes do próximo deploy. Leia em voz alta e pause — é o tipo de texto que o aluno vai escrever no capstone.
-->

- **Postura geral** — "a CredSim apresenta postura de segurança moderada: os principais riscos estão mapeados, mas dois exigem correção antes do lançamento."
- **Os 2 riscos mais críticos, em negócio** — dados de um cliente podem aparecer na resposta de outro (risco de multa de LGPD); o assistente pode enviar e-mails automaticamente sem revisão humana (risco de erro irreversível).
- **Próximas ações** — isolar a busca por conta em até 2 semanas; exigir confirmação humana no envio de e-mail antes do próximo deploy.
- **Segurança: nenhuma sigla, nenhuma ambiguidade** — qualquer diretor lê esse parágrafo e sabe exatamente o que decidir.

---

<!-- ═══════════ BLOCO PRÁTICO — laboratório capstone, separado do teórico ═══════════
O capstone roda o método completo sobre a CredSim (defesas OFF = alvo). Entrega: lab/aula6/checklist_avaliacao.ipynb + relatorio_modelo.md (relatório de riscos + resumo executivo).
Duração: bloco teórico ≈ 56 min (V1–V6); capstone ≈ 28 min; conclusão ≈ 6 min. O módulo (teórico + conclusão) fica em 1h–1h20.
-->

<!-- ═══ VÍDEO 7 · Capstone 1 — mapear e modelar a CredSim · ~9 min ═══  (laboratório) -->

## Prática 1 — Mapear e modelar a CredSim
_prática_

<!--
LAYOUT: screencast/diagrama da cadeia da CredSim com as fronteiras de confiança marcadas. Accent #1F53E5.
ROTEIRO: abre o capstone — aplicar o método completo sobre a CredSim (a app do curso, com defesas OFF como alvo). Passos 1–2: desenhe a cadeia (modelo, orquestração, ferramentas, dados) e identifique as arquiteturas (chat? RAG? agente? multi-agent?); marque as fronteiras de confiança e aplique STRIDE em cada uma. 'Você já conhece a CredSim — o objetivo é formalizar esse conhecimento num diagrama/lista estruturada.'
-->

- **Objetivo** — aplicar os passos 1–2 do método: entender o sistema e levantar ameaças.
- **Passos** — desenhe a cadeia e as arquiteturas da CredSim; marque as fronteiras de confiança e aplique STRIDE.

---

## Mapear e modelar — o que observar
_prática_

<!--
LAYOUT: 2 bullets de fechamento; liga com os vídeos 2 e 3. Accent #1F53E5.
ROTEIRO: feche a etapa 1 do capstone. Formalize o que você já sabe da CredSim num diagrama/lista — sem esse mapa não dá para avaliar. E seja sistemático: componente por componente, sem pular — 'resistência ao atalho é uma habilidade de segurança; o atacante não pula componentes'. Anote cada achado já no formato estruturado.
-->

- **Formalize o que você já sabe** — a CredSim é conhecida; estruture num diagrama/lista.
- **Seja sistemático** — componente por componente, sem pular (o atacante não pula).

---

<!-- ═══ VÍDEO 8 · Capstone 2 — checklist e documentação · ~10 min ═══  (laboratório) -->

## Prática 2 — Checklist e documentação
_prática_

<!--
LAYOUT: screencast do checklist por componente + a matriz de risco preenchida. Accent #1F53E5.
ROTEIRO: passos 3–4 sobre a CredSim. Percorra o checklist por componente (entrada, system prompt, modelo, saída, ferramentas, RAG, monitoramento); para cada 'não', você tem um achado. Anote cada um no formato estruturado (componente, OWASP, cenário, severidade) e monte a matriz de risco impacto × probabilidade. 'Não precisa ser perfeito; 4–6 achados bem documentados já são um entregável profissional.'
-->

- **Objetivo** — aplicar os passos 3–4: checar controles e documentar os achados.
- **Passos** — percorra o checklist; anote cada achado (componente, OWASP, cenário, severidade) e monte a matriz de risco.

---

## Checklist e documentação — o que observar
_prática_

<!--
LAYOUT: 2 bullets de fechamento; liga com os vídeos 4 e 5. Accent #1F53E5.
ROTEIRO: feche a etapa 2. Onde o checklist encontra uma célula de controle vazia, há um achado — priorize por impacto × probabilidade. Reforce que uma matriz com 4–6 achados bem documentados, cada um com cenário e recomendação, já é um relatório de segurança real.
-->

- **Célula vazia = gap** — onde falta controle há achado; priorize por impacto × probabilidade.
- **Entregável profissional** — 4–6 achados bem documentados já é um relatório real.

---

<!-- ═══ VÍDEO 9 · Capstone 3 — o resumo executivo · ~9 min ═══  (laboratório) -->

## Prática 3 — O resumo executivo (capstone)
_prática_

<!--
LAYOUT: screencast do relatorio_modelo.md; foco no resumo executivo de 1 página. Accent #1F53E5.
ROTEIRO: o entregável mais desafiador e mais valioso — o resumo executivo para um 'diretor' não técnico da CredSim. No máximo uma página: postura geral, 2–3 riscos mais críticos em linguagem de negócio, próximas ações. 'Se você consegue escrever esse resumo claramente, está pronto para atuar profissionalmente em LLM Security.' Entrega final: o notebook checklist_avaliacao.ipynb + o relatorio_modelo.md.
-->

- **Objetivo** — escrever o resumo executivo para um "diretor" não técnico da CredSim.
- **Passos** — em 1 página: postura geral, 2–3 riscos críticos em linguagem de negócio, próximas ações.

---

## Resumo executivo — o que observar
_prática_

<!--
LAYOUT: 2 bullets de fechamento; celebração contida do capstone concluído. Accent #1F53E5.
ROTEIRO: feche o capstone. A virada profissional: clareza + priorização + linguagem de negócio é o que faz o risco sair do relatório e ser corrigido. A entrega de ponta a ponta (mapa + threat model + checklist + achados priorizados + resumo executivo) é o produto que separa quem conhece riscos de quem sabe avaliar.
-->

- **Segurança: a virada profissional** — clareza + priorização + linguagem de negócio é o que faz o risco ser corrigido.
- **Entrega final** — `checklist_avaliacao.ipynb` + `relatorio_modelo.md`: a avaliação de ponta a ponta.

---

<!-- ═══ VÍDEO 10 · Conclusão — o método, e o fim da trilha · ~6 min ═══  (conclusão do curso) -->

## Conclusão — o método, e o fim da trilha
_conclusão_

<!--
LAYOUT: slide de síntese do curso inteiro (o arco das 6 aulas); fecho da trilha em destaque. Accent #1F53E5.
ROTEIRO: retome a frase central — segurança de LLM não é uma lista para decorar, é um método: entender → modelar → checar → priorizar → comunicar; escala do chatbot simples ao multi-agente (mudam os componentes e as fronteiras, o processo é o mesmo). O profissional formado avalia com estrutura em vez de temer o LLM. Recapitule o arco (Aula 1 vocabulário/cadeia; 2 os 10 riscos; 3 arquiteturas; 4 ataques; 5 defesas; 6 método). Este é o Curso 1 da trilha — o alicerce. Fechamento caloroso: você está pronto para avaliar aplicações de LLM reais.
-->

- **É método** — não é decorar 10 riscos: entender → modelar → checar → priorizar → comunicar.
- **Avalia, não teme** — o profissional formado avalia com estrutura em vez de temer o LLM.
- **O mapa da trilha** — vocabulário, riscos, arquiteturas, ataques, defesas e método: o que o Curso 1 entrega.
- **Fim do curso** — pronto para avaliar aplicações de LLM reais.
