Aula 6 — Avaliando a segurança de uma aplicação de LLM
1. Framework de avaliação de segurança para aplicações de LLM
O que é: um processo estruturado e repetível para medir a postura de segurança de uma app de LLM — em vez de "olhar e achar". Ele costura tudo que vimos:

Os 6 passos do framework:

Entender o sistema → mapear a cadeia (Aula 1: modelo → orquestração → ferramentas → dados) e identificar a arquitetura (Aula 3: é chat? RAG? agente? multi-agent?).
Mapear a superfície de ataque → quais camadas da cadeia estão "acesas".
Levantar as ameaças → aplicar o OWASP Top 10 2025 (Aula 2) + threat modeling (tópico 2).
Avaliar os controles existentes → checar as 5 camadas de defesa (Aula 5): a defesa em profundidade está presente?
Priorizar os riscos → por impacto × probabilidade.
Documentar e recomendar → (tópicos 4 e 5).
🔑 A lógica: a arquitetura define os riscos (Aula 3), e você avalia se os controles (Aula 5) cobrem os riscos (Aula 2). O framework é só essa pergunta, feita de forma disciplinada.

2. Threat modeling para IA: adaptando o STRIDE
O que é: threat modeling é perguntar, sistematicamente, "o que pode dar errado?" para cada componente. O STRIDE (da Microsoft) é o checklist clássico — e ele se adapta lindamente ao mundo LLM:

Letra do STRIDE	No mundo LLM	OWASP 2025
Spoofing (passar-se por outro)	injeção que faz o modelo assumir outra persona / ignorar o system prompt	LLM01
Tampering (adulterar)	envenenar dados de treino/RAG, manipular o contexto	LLM04, LLM08
Repudiation (negar autoria)	sem logs, não dá pra provar o que o agente fez	(liga ao monitoramento, Aula 5)
Information disclosure	vazar dados sensíveis, system prompt, PII	LLM02, LLM07
Denial of service	consumo sem limite, denial of wallet	LLM10
Elevation of privilege	o modelo faz mais do que deveria via ferramentas	LLM06
O processo: desenhe o fluxo de dados do sistema, marque as fronteiras de confiança (trust boundaries) — e aqui está o ponto crítico para LLM: como a fronteira instrução×dado é borrada (Aula 1), toda entrada de dado não-confiável (input do usuário, doc de RAG, saída de ferramenta, mensagem de outro agente) é uma fronteira que merece atenção. Aplique STRIDE em cada uma.

3. Revisão de arquitetura de segurança: checklist por componente
O que é: percorrer a cadeia (Aula 1) componente por componente, com perguntas fixas. É o framework do tópico 1 virando uma lista prática:

Entrada / usuário: há autenticação e autorização? rate limiting? separação de confiança? (LLM10, LLM01)
System prompt: contém segredos (não deveria)? a segurança depende dele? (LLM07)
Modelo: proprietário ou self-hosted? proveniência verificada? os dados saem para um terceiro? (LLM03, Aula 4)
Saída: é tratada como não-confiável? há sanitização/encoding? filtro de egress/PII? (LLM05, LLM02)
Ferramentas: menor privilégio? human-in-the-loop para ação de alto impacto? parâmetros validados? (LLM06)
Dados / RAG: controle de acesso por usuário antes da recuperação? índice sanitizado? isolamento de tenant? (LLM08, LLM02)
Monitoramento: há logs? detecção de anomalias? red-teaming periódico? (LLM10 + detecção geral)
🔑 Cada linha cruza os 3 eixos do curso: um componente (Aula 1), um risco (Aula 2) e um controle (Aula 5). Se uma célula está vazia, você achou um gap.

4. Documentando riscos e recomendações
O que é: transformar os achados em um relatório rastreável, priorizado e acionável.

Estrutura de cada achado:

Descrição + componente afetado + categoria OWASP.
Cenário de exploração (como um atacante usaria).
Severidade = impacto × probabilidade.
Recomendação específica e esforço estimado.
Priorização: uma matriz de risco (impacto × probabilidade) decide a ordem de ataque.

⚠️ Recomendação ruim: "seja mais seguro". Recomendação boa: "adicione confirmação humana na ferramenta de envio de e-mail (LLM06), pois hoje o agente a aciona sozinho." Específica, ligada ao risco, acionável.

5. Como apresentar riscos para stakeholders não técnicos
O que é: traduzir risco técnico em linguagem de negócio. O executivo não quer saber o que é "prompt injection" — quer saber o impacto.

Fale em consequência de negócio: perda financeira, vazamento de dados de cliente, multa de LGPD, dano reputacional.
Use analogias e o gradiente capacidade×impacto (como fizemos no curso): "o assistente pode encaminhar e-mails sozinho — um atacante explora isso sem nunca falar com ele."
Apresente o pior cenário realista, a probabilidade e o custo de mitigar vs. o risco.
Evite FUD (vender medo). Seja objetivo; use a matriz visual; entregue recomendações priorizadas com trade-offs.
🔑 Essa é uma habilidade profissional decisiva: o melhor achado técnico é inútil se o decisor não entende por que deve investir em corrigi-lo.

6. Laboratório: avaliação estruturada sobre uma aplicação fictícia
O que é: o exercício-capstone — pegar uma app de LLM fictícia e rodar o framework inteiro sobre ela:

Mapear a cadeia e a arquitetura.
Fazer threat modeling (STRIDE + OWASP 2025).
Rodar o checklist por componente.
Documentar os riscos priorizados (matriz).
Escrever recomendações + um resumo executivo para não-técnicos.
💡 Conexão direta: é exatamente aqui que a aplicação prática que discutimos (o "lab vivo" vulnerável) encaixa como objeto do laboratório — o aluno avalia aquele sistema. Ou seja: o app que vamos construir vira o estudo de caso da Aula 6.

A história da Aula 6 — e do curso inteiro
A Aula 6 é o funil onde tudo deságua:

Etapa	Vem de qual aula
Entender o sistema (cadeia + arquitetura)	Aulas 1 e 3
Modelar ameaças (STRIDE + OWASP)	Aulas 2 e 6
Avaliar controles	Aula 5
Considerar dados/privacidade/LGPD	Aula 4
Documentar e comunicar	Aula 6
🔑 Mensagem final do curso: segurança de LLM não é decorar 10 riscos — é um método: entender a cadeia → modelar as ameaças por componente → verificar se os controles cobrem → priorizar → comunicar. O profissional formado por este curso não "tem medo de LLM": ele avalia um sistema de LLM com estrutura e o explica para quem decide.

✅ Checks de entendimento
Por que fronteiras de confiança (trust boundaries) são o conceito mais importante do threat modeling especificamente para LLMs? (Dica: Aula 1, fronteira instrução×dado.)
No STRIDE adaptado, a que risco OWASP 2025 corresponde "Elevation of Privilege" num agente — e qual controle da Aula 5 o ataca?
Você encontrou 8 riscos numa avaliação. Como decide qual reportar primeiro ao cliente, e como explica isso a um diretor não técnico?
🎓 Com isso, cobrimos as 6 aulas do curso. Você agora tem o material de estudo completo (Aulas 1–6) nas suas notas. Quando quiser, retomamos a aplicação prática (motor mock + opção de API real, já decidido) — e ela serve tanto de exemplo ao longo das aulas quanto de objeto do laboratório da Aula 6. É só dizer.