# Aula 6 — Roteiro falado (teleprompter)

> **Voz calibrada no padrão da Aula 1** (`aula1/recursos/aula1_roteiro_falado.md`, calibrado na transcrição real do professor gravando) — conectores dominantes: "então", "falando sobre X, né?" e "nós" (mais que "vocês") nas partes teóricas; "vocês" reservado para a instrução direta no capstone prático. Esta é a última aula do curso: o fechamento do vídeo final encerra a trilha, sem gancho para "próxima aula".

**Como usar:**
- **Grave slide a slide** (~40–60s cada).
- **`[pausa]` = respire.** Silêncio é editável.
- **Internalize o exemplo, não as palavras.**
- **Travou? Recomece a frase** — corta na edição.

---

## VÍDEO 1 · Abertura — de conhecimento a método · ~5 min

**Slide — Capa (Aula 6)**
> Olá. Bem-vindos à sexta e última aula do curso de LLM Security. Nesta aula, nós juntamos tudo que construímos até aqui — o vocabulário da Aula 1, os riscos da Aula 2, as arquiteturas da Aula 3, os ataques da Aula 4 e as defesas da Aula 5 — num processo de avaliação que funciona em qualquer aplicação de LLM. E o diferencial profissional está aqui também: avaliar não basta, é preciso comunicar o risco para quem decide. Vamos começar.

**Slide — O que veremos nesta aula**
> Falando sobre o que vamos ver nesta aula, né? Então, primeiro vem o método de avaliação: um processo de quatro passos — entender, modelar, checar e priorizar — que se aplica em qualquer aplicação de LLM. Depois, o STRIDE adaptado ao LLM, que é o modelo de ameaças da Microsoft ajustado pra nossa realidade, ligando cada letra ao OWASP 2025. Em seguida, como documentar cada achado e escrever um resumo executivo que um diretor não técnico entende. E, para fechar, o laboratório: aplicamos o método inteiro sobre a CredSim, a aplicação do curso.

---

## VÍDEO 2 · Método de avaliação de segurança · ~10 min

**Slide — Um método de avaliação de segurança**
> Vamos falar do método de avaliação de segurança — um processo de quatro passos. O primeiro é entender o sistema: antes de procurar qualquer vulnerabilidade, nós precisamos entender o que estamos avaliando. Isso significa mapear a cadeia — modelo, orquestração, ferramentas e dados, que vimos lá na Aula 1 — e identificar a arquitetura: é um chat simples? Tem RAG? Tem agente executando ação, como vimos na Aula 3? Sem esse mapa, nós nem sabemos onde procurar. [pausa] O segundo passo é levantar ameaças. Com o mapa em mãos, o OWASP Top 10 2025, que vimos na Aula 2, é o ponto de partida — aquele documento de conscientização que já conhecemos. E o threat modeling, que é o próximo vídeo, sistematiza esse levantamento.

**Slide — Método de avaliação — checar e priorizar**
> Falando sobre o passo 3, né? Avaliar controles. Levantar ameaças sem olhar os controles é meio trabalho só — então nós checamos as cinco camadas de defesa em profundidade que vimos na Aula 5, uma por uma. A pergunta central aqui é simples: cada risco que levantamos tem um controle correspondente? [pausa] E o passo 4 é priorizar. Nem todo risco merece a mesma urgência, então a matriz de impacto vezes probabilidade decide a ordem. E é aqui que o método fecha: a arquitetura, no passo 1, define quais riscos são mais prováveis; o checklist, no passo 3, mostra onde falta controle; e a priorização junta as duas coisas.

**Slide — Método em ação — um mini-exemplo na CredSim**
> Para fechar o método, vamos ver ele em ação, num mini-exemplo rápido na CredSim. Pega o componente Suporte, que é o RAG da aplicação: ele responde pergunta do cliente puxando documento de um índice vetorial único, compartilhado entre todas as contas. [pausa] Passo 1, entender, é justamente isso. Passo 2, levantar ameaças: o risco mais provável aqui é o LLM08, vazamento entre tenants, porque o índice não separa por conta. Passo 3, avaliar controles: ao checar as cinco camadas de defesa da Aula 5, não existe filtro de tenant na busca vetorial — controle ausente, confirmado. E o passo 4 já vem de graça: o achado nasce priorizado — impacto alto, porque vaza dado de cliente, vezes probabilidade alta, porque acontece em qualquer busca, dá crítico. É o mesmo exercício que vai aparecer no laboratório desta aula — aqui eu guio passo a passo.

---

## VÍDEO 3 · Threat modeling — STRIDE adaptado · ~11 min

**Slide — Threat modeling — STRIDE adaptado ao LLM**
> Vamos falar de threat modeling, que é a modelagem de ameaças, usando o STRIDE adaptado ao LLM. STRIDE é um acrônimo da Microsoft — Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service e Elevation of Privilege. Em português: falsificação de identidade, adulteração, repúdio, vazamento de informação, negação de serviço e elevação de privilégio. Não é uma ferramenta nova, é um checklist mental de ameaças, e funciona bem quando o adaptamos ao LLM. Então vamos ligar cada letra ao OWASP 2025: Tampering vira LLM04, que é envenenar o modelo, e LLM08, que é envenenar o RAG. Information Disclosure vira LLM02, vazar dados, e LLM07, o system prompt. Denial of Service vira LLM10, consumo ilimitado. E Elevation of Privilege vira LLM06, agência e ferramentas. [pausa] Já Spoofing e Repudiation são transversais — dependem de autenticação e de logs, não são específicos do LLM. Ainda importam, fazem parte da segurança de aplicações em geral, mas não têm um LLM0X dedicado como as outras letras.

**Slide — Threat modeling — fronteiras de confiança**
> E aqui chegamos num ponto central desta aula: a fronteira de confiança. Lembram lá da Aula 1, quando vimos que a parede entre instrução e dado no LLM quase não existe? Então, toda entrada não confiável é uma fronteira que precisa ser mapeada — o texto que o usuário digita, um documento indexado no RAG, a resposta que vem de uma ferramenta, a mensagem de outro agente. [pausa] Para operacionalizar isso, nós desenhamos o fluxo de dados — quem manda o quê para quem —, marcamos cada fronteira, e em cada uma perguntamos: qual letra do STRIDE pode acontecer aqui? Esse é o exercício central do laboratório desta aula.

**Slide — STRIDE em ação — a fronteira que ninguém tinha marcado**
> Vamos ver esse exercício acontecendo de verdade, com um cenário da CredSim. No primeiro diagrama que o time desenhou, o fluxo ia do usuário para o modelo e daí para a resposta; o documento indexado no RAG entrou como "dado interno" — sem virar uma fronteira de confiança marcada, porque parecia inofensivo, estava "dentro de casa". [pausa] Na revisão com o STRIDE, alguém faz a pergunta certa: essa fronteira permite Tampering, ou seja, adulteração? E a resposta é sim — um documento malicioso indexado ali altera a resposta para todo cliente que recuperar aquele trecho, o que é LLM04 e LLM08 ao mesmo tempo. A fronteira esquecida vira achado formal: falta validação de conteúdo antes de indexar. Segurança: toda fronteira conta, mesmo a que parece interna — dado indexado também é entrada não confiável.

---

## VÍDEO 4 · Revisão de arquitetura — checklist por componente · ~11 min

**Slide — Checklist por componente — entrada e saída**
> Vamos falar da revisão de arquitetura: o checklist por componente. A ideia é percorrer cada peça da cadeia fazendo as perguntas certas. Começando pela entrada, o system prompt e o modelo: há autenticação e autorização implementadas? Existe rate limit contra abuso, que é LLM10, e contra flooding de prompt, que é LLM01? O system prompt guarda algum segredo, ou a segurança depende dele continuar secreto — isso é LLM07? E a proveniência do modelo foi verificada — de onde ele veio, se foi ajustado por alguém, o risco de supply chain, que é LLM03? [pausa] Agora, saída, ferramentas e RAG: a saída é tratada como não confiável e sanitizada antes de renderizar ou executar — isso é LLM05? As ferramentas seguem o menor privilégio, com confirmação humana para ação irreversível — LLM06? E no RAG existe isolamento de tenant, ou seja, um usuário não recupera documento de outro — LLM08? Cada "não" que aparece aqui já é um achado.

**Slide — Checklist por componente — a matriz que amarra o curso**
> Falando de monitoramento, né? Uma aplicação segura no deploy não garante segurança em produção. Então perguntamos: há logs suficientes para investigar um incidente? Existe detecção de anomalia — volume incomum, padrão de injeção, resposta fora do perfil? Há red-teaming periódico? Isso cobre o consumo de recursos, LLM10, e a detecção geral de comportamento anômalo. [pausa] E aqui as três aulas se encontram: cada linha desse checklist cruza exatamente três eixos — um componente da cadeia, que é a Aula 1; um risco do OWASP 2025, que é a Aula 2; e um controle de defesa em profundidade, que é a Aula 5. Quando vocês montam essa tabela para uma aplicação real e encontram uma célula de controle vazia, encontraram um gap.

**Slide — Checklist em ação — a célula vazia que virou achado**
> Vamos ver essa matriz em ação, com um caso real no componente API da CredSim. A pergunta do checklist é direta: existe rate limit e quota por usuário? [pausa] E a resposta, ao inspecionar a configuração, é não — qualquer chave de API autenticada pode disparar milhares de chamadas sem limite nenhum. Na matriz componente, risco e controle, a linha "API, LLM10, rate limit" fica com a célula de controle vazia — um gap real, encontrado, não hipotético. Segurança: célula vazia vira achado na hora — não é só uma observação que fica anotada para depois, ela já entra no relatório com severidade e recomendação no mesmo instante.

---

## VÍDEO 5 · Documentar riscos e recomendações · ~10 min

**Slide — Documentar — a anatomia de um achado**
> Vamos falar de documentar riscos e recomendações. Encontrar o risco é metade do trabalho — documentar bem é o que torna a avaliação útil de verdade. Então cada achado tem uma estrutura mínima: descrição, componente afetado, categoria do OWASP 2025, cenário de exploração, severidade e recomendação. E o cenário de exploração precisa ser concreto, não abstrato — é o campo que convence quem lê. [pausa] Com vários achados na mão, nós precisamos priorizar: a matriz de impacto vezes probabilidade decide a ordem. Alto e alto é crítico, corrige já; alto impacto e baixa probabilidade, monitora; baixo impacto e alta probabilidade vai para o backlog. Uma tabela três por três, simples assim, já comunica prioridade.

**Slide — Documentar — um achado completo, campo a campo**
> Vamos preencher essa estrutura com um achado real da CredSim, campo a campo. Descrição e componente: o agente de suporte aciona a ferramenta de envio de e-mail sem nenhuma confirmação humana — o componente afetado é ferramentas e agente. [pausa] Categoria e cenário de exploração: isso é LLM06, excessive agency, agência excessiva; o cenário é uma injeção escondida dentro de um ticket, que faz o agente enviar automaticamente um e-mail com dado de cliente para um endereço externo. Severidade e recomendação: alta, porque o impacto é alto e a probabilidade é média; a recomendação é exigir confirmação humana explícita antes de qualquer envio. Segurança: o cenário é o que convence — sem ele, esse achado parece teórico; com ele, qualquer leitor entende o risco real.

**Slide — Documentar — recomendação acionável**
> E toda essa documentação só vale a pena se a recomendação for acionável. Uma recomendação ruim é vaga — algo como "seja mais seguro". Isso não diz nada. Uma recomendação boa é específica e firme — "adicione confirmação humana na ferramenta de envio de e-mail, referente ao LLM06, porque hoje o agente aciona ela sozinho". [pausa] Repara a diferença: a boa recomendação tem três atributos — é específica, diz qual componente e qual mudança; está ligada ao risco, referenciando o LLM0X e o cenário; e é acionável, diz quem faz o quê. Uma recomendação acionável é aquela que um desenvolvedor pega amanhã e implementa sem precisar te ligar de volta.

---

## VÍDEO 6 · Apresentar riscos a stakeholders não técnicos · ~9 min

**Slide — Apresentar a quem decide — linguagem de negócio**
> Vamos falar de apresentar riscos para quem decide. O erro mais comum de quem trabalha com segurança técnica é entregar um relatório cheio de sigla que o tomador de decisão não entende — e aí nada é corrigido. [pausa] Traduzir para negócio não é simplificar, é respeitar quem está do outro lado: perda financeira, vazamento de dado de cliente, multa de LGPD, dano reputacional. Por exemplo: dizer "LLM07 exposto" não diz nada para um diretor. Mas dizer "um atacante extrai as instruções do sistema em 30 segundos, e isso dá a ele o roteiro completo para contornar todos os filtros" — isso ele entende. E cuidado com o FUD — medo, incerteza e dúvida: não é para exagerar nem vender medo, é para ser preciso sobre o impacto real.

**Slide — Apresentar a quem decide — o resumo executivo**
> E isso tudo converge para o resumo executivo. Ele é escrito para o diretor de produto, para o CTO ou para o cliente — para quem não vai ler o relatório técnico inteiro. No máximo uma página: qual é a postura geral de segurança, quais são os dois ou três riscos mais críticos em linguagem de negócio, e quais são as próximas ações. [pausa] Se vocês conseguem escrever esse resumo com clareza, já estão prontos para atuar profissionalmente em LLM Security.

**Slide — O resumo executivo — um exemplo real (CredSim)**
> Vamos ver esse modelo preenchido com um resumo executivo real da CredSim. Postura geral: "a CredSim apresenta postura de segurança moderada — os principais riscos estão mapeados, mas dois deles exigem correção antes do lançamento." [pausa] Os dois riscos mais críticos, já em linguagem de negócio: dados de um cliente podem aparecer na resposta de outro cliente, o que é risco de multa de LGPD; e o assistente pode enviar e-mails automaticamente sem nenhuma revisão humana, o que é risco de erro irreversível. Próximas ações: isolar a busca por conta em até duas semanas, e exigir confirmação humana no envio de e-mail antes do próximo deploy. Segurança: nenhuma sigla, nenhuma ambiguidade — qualquer diretor lê esse parágrafo e sabe exatamente o que decidir. É esse tipo de texto que vai aparecer de novo no capstone.

---

## VÍDEO 7 · Capstone 1 — mapear e modelar a CredSim · ~9 min

**Slide — Prática 1 — Mapear e modelar a CredSim**
> Vamos para o primeiro capstone: aplicar o método inteiro sobre a CredSim, a aplicação do curso, com as defesas desligadas como alvo. O objetivo aqui é aplicar os passos 1 e 2: entender o sistema e levantar ameaças. Então, desenhem a cadeia da CredSim — modelo, orquestração, ferramentas e dados — e identifiquem as arquiteturas envolvidas: tem chat? Tem RAG? Tem agente? Tem multi-agente? Depois, marquem as fronteiras de confiança e apliquem o STRIDE em cada uma. Vocês já conhecem a CredSim; o objetivo agora é formalizar esse conhecimento num diagrama ou numa lista estruturada.

**Slide — Mapear e modelar — o que observar**
> Fechando essa primeira etapa: formalizem o que vocês já sabem da CredSim num diagrama ou numa lista — sem esse mapa, não dá para avaliar depois. [pausa] E sejam sistemáticos: componente por componente, sem pular nenhum. Resistir ao atalho é uma habilidade de segurança — o atacante não pula componente, então o avaliador também não pode pular. Já vão anotando cada achado no formato estruturado, porque vocês vão precisar dele no próximo vídeo.

---

## VÍDEO 8 · Capstone 2 — checklist e documentação · ~10 min

**Slide — Prática 2 — Checklist e documentação**
> Vamos para a segunda etapa do capstone: com o mapa em mãos, apliquem os passos 3 e 4 — checar os controles e documentar os achados. Percorram o checklist por componente: entrada, system prompt, modelo, saída, ferramentas, RAG, monitoramento. Para cada "não" que aparecer, vocês têm um achado. Anotem cada um no formato estruturado — componente, OWASP, cenário, severidade — e montem a matriz de risco de impacto vezes probabilidade. [pausa] Não precisa ser perfeito: quatro a seis achados bem documentados já são um entregável profissional.

**Slide — Checklist e documentação — o que observar**
> Fechando essa etapa: onde o checklist encontrou uma célula de controle vazia, ali está um achado — é a matriz componente, risco e controle que vimos na teoria, agora em ação na CredSim. Priorizem por impacto vezes probabilidade. E vale reforçar: uma matriz com quatro a seis achados bem documentados, cada um com cenário e recomendação, já é um relatório de segurança real — o produto que um profissional entrega.

---

## VÍDEO 9 · Capstone 3 — o resumo executivo · ~9 min

**Slide — Prática 3 — O resumo executivo (capstone)**
> Vamos para a terceira e última etapa do capstone: o entregável mais desafiador, e também o mais valioso. Escrevam o resumo executivo para um "diretor" não técnico da CredSim. Em no máximo uma página: qual é a postura geral de segurança, quais são os dois ou três riscos mais críticos em linguagem de negócio, e quais são as próximas ações. Usem o relatorio_modelo.md como modelo. [pausa] Se vocês conseguem escrever esse resumo com clareza, estão prontos para atuar profissionalmente em LLM Security. A entrega final é o notebook checklist_avaliacao.ipynb junto com o relatorio_modelo.md.

**Slide — Resumo executivo — o que observar**
> E aqui está a virada profissional: clareza, priorização e linguagem de negócio são o que faz o risco sair do relatório e virar correção de verdade. [pausa] Vocês entregaram, de ponta a ponta: o mapa, o threat model, o checklist, os achados priorizados e o resumo executivo. Esse é o produto que separa quem conhece os riscos de quem sabe avaliar.

---

## VÍDEO 10 · Conclusão — o método, e o fim da trilha · ~6 min

**Slide — Conclusão — o método, e o fim da trilha**
> Vamos amarrar o curso. E vale retomar a frase central desta aula: segurança de LLM não é uma lista para decorar — é um método. Entender, modelar, checar, priorizar e comunicar. Esse método escala: do chatbot mais simples ao sistema multi-agente mais complexo, mudam os componentes e as fronteiras, mas o processo é sempre o mesmo. [pausa] O profissional que passa por este curso não é aquele que sabe que LLM é perigoso — isso todo mundo já sabe. É aquele que sabe avaliar. A diferença entre a ansiedade e a competência é estrutura: vocês têm estrutura agora para sentar na frente de qualquer aplicação de LLM, fazer as perguntas certas e produzir uma avaliação fundamentada. [pausa] Recapitulando rapidamente o arco deste curso: na Aula 1, nós vimos o vocabulário e a cadeia; na Aula 2, os dez riscos do OWASP 2025; na Aula 3, como a arquitetura define os riscos; na Aula 4, os riscos de dados e privacidade; na Aula 5, as defesas em profundidade; e nesta Aula 6, tudo isso virou um método de avaliação. Este foi o Curso 1 da trilha de LLM Security — o alicerce sobre o qual o resto se constrói. [pausa] Então, fica o fechamento: vocês estão prontos para avaliar aplicações de LLM reais — a aplicação da empresa de vocês, um projeto open source, o sistema que vocês ainda vão construir. O processo está com vocês agora. Muito obrigado pela presença ao longo dessas seis aulas.
