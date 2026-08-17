Trilha: LLM Security
Curso 1: LLM Security: riscos em modelos de linguagem
Modelos de linguagem de grande escala estão sendo integrados a produtos, pipelines
corporativos e infraestruturas críticas em uma velocidade que está superando a
capacidade de avaliação de risco das organizações. Sistemas de IA que respondem a
clientes, que acessam bancos de dados, que executam ações em nome de usuários e que
processam documentos internos confidenciais já são realidade em empresas de todos os
tamanhos. E com eles chegam vetores de ataque completamente novos que os frameworks
tradicionais de segurança não foram projetados para cobrir.
Este curso constrói o mapa de ameaças que orienta toda a trilha. Você vai entender como
LLMs funcionam do ponto de vista de segurança, quais são as superfícies de ataque que
eles introduzem, como o OWASP Top 10 para LLMs organiza esses riscos e quais são as
estratégias de defesa e mitigação para cada categoria. É o curso que dá vocabulário,
estrutura e contexto para tudo que vem a seguir.
Objetivos de aprendizagem
• Compreender como LLMs funcionam internamente no nível necessário para avaliar
seus riscos de segurança
• Identificar as principais superfícies de ataque introduzidas por sistemas baseados
em LLMs em ambientes corporativos
• Aplicar o OWASP Top 10 para LLMs como framework de referência para avaliação de
risco em aplicações de IA
• Reconhecer os riscos específicos de arquiteturas com agentes, RAG e integração de
ferramentas externas
• Descrever as principais estratégias de mitigação para cada categoria de risco em
LLMs
• Avaliar a postura de segurança de uma aplicação baseada em LLM usando critérios
estruturados
Aula 1: Como LLMs funcionam e por que isso importa para segurança
• Transformers, tokens e geração de texto: o que o profissional de segurança precisa
entender sem precisar de matemática avançada
• O papel do treinamento, do fine-tuning e do RLHF na formação do comportamento
do modelo
• System prompts, user prompts e contexto: como a entrada moldura o que o modelo
responde
• Por que LLMs não têm memória persistente e o que isso significa para a segurança
• Modelos proprietários vs. modelos open source: diferenças de superfície de ataque
• A cadeia de dependências de um sistema baseado em LLM: modelo, orquestração,
ferramentas e dados
Aula 2: OWASP Top 10 para LLMs
• Por que o OWASP criou um Top 10 específico para LLMs e como usá-lo
• LLM01: Prompt Injection, a ameaça mais prevalente e suas variações
• LLM02: Insecure Output Handling, quando a saída do modelo chega a sistemas que
a executam
• LLM03: Training Data Poisoning, manipulando o comportamento via dados de
treinamento
• LLM04: Model Denial of Service, exaurindo recursos com entradas especialmente
elaboradas
• LLM05: Supply Chain Vulnerabilities, os riscos dos componentes que cercam o
modelo
• LLM06 ao LLM10: Sensitive Information Disclosure, Insecure Plugin Design,
Excessive Agency, Overreliance e Model Theft
Aula 3: Superfícies de ataque em arquiteturas com LLMs
• Aplicações de chat: a superfície mais simples e ainda assim cheia de vetores
exploráveis
• RAG (Retrieval Augmented Generation): riscos de envenenamento de base de
conhecimento e exfiltração via recuperação
• Agentes com ferramentas: quando o LLM pode executar ações no mundo e o que
isso significa para o perímetro de segurança
• Multi-agent systems: como a confiança entre agentes cria cadeias de
comprometimento
• LLMs em pipelines de código: modelos que geram ou revisam código e os riscos de
execução
• APIs de LLM expostas: autenticação, autorização e rate limiting em endpoints de IA
Aula 4: Riscos de dados e privacidade em sistemas de LLM
• Memorização de dados de treinamento: como modelos podem vazar informações
do conjunto de dados original
• Exfiltração de dados via interação com o modelo: extraindo informações que não
deveriam estar acessíveis
• Riscos de privacidade em RAG: quando os documentos recuperados contêm dados
sensíveis de outros usuários
• Dados enviados a APIs externas de LLM: o que acontece com os prompts e como
proteger dados sensíveis
• LGPD e IA: as implicações regulatórias do processamento de dados pessoais por
modelos de linguagem
• Avaliando a política de uso de dados dos principais provedores de LLM
Aula 5: Mitigações e controles de segurança para LLMs
• Defesa em profundidade para sistemas de LLM: controles em cada camada da
arquitetura
• Input validation e sanitização de prompts: o que funciona e o que não funciona
• Output validation: verificando a saída do modelo antes de usá-la em sistemas
downstream
• Princípio do menor privilégio para agentes: limitando o que o modelo pode fazer e
acessar
• Guardrails: ferramentas e técnicas para restringir o comportamento do modelo em
produção
• Monitoramento de sistemas de LLM em produção: o que registrar e o que alertar
Aula 6: Avaliando a segurança de uma aplicação de LLM
• Framework de avaliação de segurança para aplicações de LLM: o que olhar e como
estruturar a análise
• Threat modeling para sistemas de IA: adaptando o STRIDE para o contexto de LLMs
• Revisão de arquitetura de segurança: checklist por componente
• Documentando riscos e recomendações para equipes que desenvolvem ou operam
sistemas de LLM
• Como apresentar riscos de LLM para stakeholders não técnicos: linguagem, impacto
de negócio e priorização
• Laboratório: conduzindo uma avaliação estruturada de segurança sobre uma
aplicação de LLM fictícia