Aula 2 — OWASP Top 10 para LLMs
Por que o OWASP criou um Top 10 só para LLMs (e como usar)
O OWASP é uma organização famosa por listas de riscos de segurança — o "OWASP Top 10" clássico (de aplicações web) é referência mundial. Mas aquele Top 10 foi pensado para riscos como SQL injection e XSS, e — como vimos na Aula 1 — LLMs introduzem riscos que aqueles frameworks não cobrem (a fronteira instrução×dado, o comportamento probabilístico, a cadeia de ferramentas).

Então o OWASP criou um Top 10 específico para LLMs. Para que serve, na prática:

Linguagem comum: time de segurança, devs e gestão passam a chamar os riscos pelos mesmos nomes ("isso é um LLM01").
Checklist de avaliação: ao revisar uma aplicação, você varre as 10 categorias.
Base para threat modeling (que é a Aula 6).
⚠️ Como NÃO usar: não é uma lista exaustiva nem uma "receita de bolo". É um ponto de partida — você prioriza as categorias conforme a arquitetura do seu sistema (um chatbot simples tem riscos diferentes de um agente com ferramentas).


OWASP Top 10 for LLMs — 2025 (revisado)
LLM01:2025 — Prompt Injection
O que é: fazer o modelo seguir instruções do atacante em vez das do desenvolvedor. Direta (usuário digita o ataque) ou indireta (o ataque vem escondido num dado que o modelo lê: documento, página, e-mail).
Exemplo: o e-mail com instrução invisível que faz o assistente encaminhar mensagens.
Mitigação: separar/marcar conteúdo não-confiável, menor privilégio, validação de saída, confirmação humana para ações sensíveis. (Continua nº 1 e o mais difícil — sem "conserto" definitivo.)

LLM02:2025 — Sensitive Information Disclosure (era LLM06 em 2023)
O que é: o modelo revela dados sensíveis — memorizados do treino ou presentes no contexto (system prompt, dados de outro usuário, trechos de RAG).
Exemplo: cospe PII que "decorou"; vaza dados de outro cliente num RAG mal isolado.
Mitigação: minimizar dados sensíveis no treino/contexto, scrubbing de PII, controle de acesso por usuário, nunca colocar segredos no prompt. (Subiu de posição — é o tema central da Aula 4.)

LLM03:2025 — Supply Chain (era LLM05 em 2023)
O que é: comprometimento via terceiros: modelos baixados, datasets, bibliotecas, e — novidade enfatizada em 2025 — adaptadores (LoRA), modelos de fine-tuning de hubs públicos e modelos descontinuados.
Exemplo: baixar um modelo "open weights" com backdoor; usar um adapter envenenado de um repositório público. 🔎
Mitigação: verificar origem e assinatura, fontes confiáveis, inventário de dependências (SBOM), avaliar procedência de modelos/adapters.

LLM04:2025 — Data and Model Poisoning (era LLM03 "Training Data Poisoning", agora mais amplo)
O que é: contaminar dados de treino, fine-tuning ou embeddings — ou distribuir um modelo pré-treinado já envenenado — para plantar vieses, erros ou backdoors.
Exemplo: injetar exemplos venenosos no fine-tuning criando uma "senha mágica"; publicar um modelo base comprometido. 🔎 (O nome mudou para incluir o envenenamento do próprio modelo, não só dos dados.)
Mitigação: proveniência e curadoria dos dados, validação, testes de comportamento, verificar a origem dos modelos.

LLM05:2025 — Improper Output Handling (era LLM02 "Insecure Output Handling")
O que é: confiar cegamente na saída do modelo e jogá-la em outro sistema sem tratar. A saída é texto não-confiável — em HTML, SQL, shell ou eval() abre as injeções clássicas.
Exemplo: resposta com <script>...</script> renderizada → XSS; SQL gerado e executado direto → SQL injection.
Mitigação: tratar a saída como input não-confiável — sanitizar/encodar antes de usar, nunca eval direto. (A ponte com o appsec tradicional. Só mudou "Insecure" → "Improper".)

LLM06:2025 — Excessive Agency (era LLM08; agora absorve o antigo "Insecure Plugin Design")
O que é: dar ao LLM autonomia, permissões ou funcionalidades em excesso → ele consegue causar dano real. Em 2025 essa categoria engloba também ferramentas/plugins mal projetados (excesso de funcionalidade/permissão).
Exemplo: um agente que apaga registros ou transfere dinheiro sozinho; um plugin que executa qualquer comando sem validar. 🔎
Mitigação: menor privilégio, limitar quais ferramentas existem, validar/tipar parâmetros de ferramentas, human-in-the-loop para ações de alto impacto.

LLM07:2025 — System Prompt Leakage (NOVO em 2025)
O que é: o risco de o system prompt ser extraído/vazado — e, pior, de a aplicação confiar nele para guardar segredos ou regras de segurança (credenciais, lógica de permissão) achando que está escondido.
Exemplo: o atacante extrai o system prompt e descobre uma chave de API, uma connection string ou as regras de negócio que deveriam ser secretas. 🔎
Mitigação: nunca colocar segredos/credenciais no system prompt; não depender do system prompt para controle de acesso — aplicar segurança no backend; assumir que o system prompt pode ser exposto.

LLM08:2025 — Vector and Embedding Weaknesses (NOVO em 2025 — riscos de RAG)
O que é: fraquezas em como vetores/embeddings são gerados, armazenados e recuperados em sistemas RAG.
Exemplo: documento envenenado na base vetorial; vazamento entre tenants (RAG multiusuário devolve trechos de outro cliente); inversão de embedding (recuperar o texto-fonte/PII a partir do vetor). 🔎
Mitigação: isolamento por usuário/tenant e controle de acesso no banco vetorial, validar/sanitizar dados antes de indexar, monitorar a base por conteúdo malicioso, permissões granulares de recuperação. (Conecta direto com as Aulas 3 e 4.)

LLM09:2025 — Misinformation (era LLM09 "Overreliance", reformulado)
O que é: o LLM produz informação falsa que parece confiável. Causa-raiz: alucinação. Overreliance entra como fator agravante — confiar sem verificar multiplica o impacto.
Exemplo: package hallucination (sugere pacote inexistente → atacante registra com malware → slopsquatting); citações jurídicas falsas (Mata v. Avianca); código inseguro aceito sem revisão; orientação crítica errada com tom de autoridade. 🔎
Mitigação: grounding com RAG, verificação cruzada + supervisão humana, validação automática de saída, citar fontes e comunicar limitações, secure coding.

LLM10:2025 — Unbounded Consumption (era LLM04 "Model DoS"; agora absorve parte de "Model Theft")
O que é: uso de recursos sem limites → DoS, custo explosivo ("denial of wallet") e também extração do modelo via consultas em massa (model extraction, que em 2023 era o LLM10 "Model Theft").
Exemplo: prompts gigantes/loops que estouram o custo; um concorrente que "destila" seu modelo fazendo milhares de perguntas sistemáticas. 🔎
Mitigação: rate limiting, limites de tokens e quotas por usuário, monitorar custo/uso, detectar padrões de consulta anômalos.




A grande sacada: os 10 riscos mapeiam na cadeia da Aula 1
Lembra da cadeia modelo → orquestração → ferramentas → dados? Os 10 riscos não são uma lista solta — cada um vive numa parte da cadeia:

Onde, na cadeia	Riscos OWASP que moram ali
Entrada / contexto	LLM01 (Prompt Injection), LLM07 (System Prompt Leakage)
O modelo em si	LLM04 (Data and Model Poisoning), LLM10 (Unbounded Consumption — DoS + extração)
A saída	LLM05 (Improper Output Handling), LLM09 (Misinformation), LLM02 (Sensitive Information Disclosure)*
Ferramentas	LLM06 (Excessive Agency — agora inclui plugins inseguros)
Dados / RAG (recuperação)	LLM08 (Vector and Embedding Weaknesses)
Terceiros / cadeia	LLM03 (Supply Chain)
* Riscos "cross-cutting" (vivem em mais de uma camada):

LLM02 (Sensitive Information Disclosure): o vazamento acontece na saída, mas a origem está no treino/contexto — por isso a defesa age nos dois lados (minimizar o que entra + filtrar o que sai).
LLM04 (Data and Model Poisoning): toca o "modelo", mas o ataque entra pelos dados (treino, fine-tuning, embeddings).
🔑 A leitura continua a mesma da Aula 1 — a superfície de ataque é a cadeia inteira — mas agora a 2025 deixa a camada de dados/RAG explícita (LLM08), que em 2023 estava diluída.

Código 2025	Risco	Mudança vs. 2023
LLM01	Prompt Injection	mantém o nº 1
LLM02	Sensitive Information Disclosure	subiu (era LLM06)
LLM03	Supply Chain	subiu (era LLM05)
LLM04	Data and Model Poisoning	renomeado/ampliado (era "Training Data Poisoning")
LLM05	Improper Output Handling	renomeado (era LLM02 "Insecure Output Handling")
LLM06	Excessive Agency	subiu (era LLM08)
LLM07	System Prompt Leakage	novo em 2025
LLM08	Vector and Embedding Weaknesses	novo — riscos de RAG/embeddings
LLM09	Misinformation	novo (absorve parte de "Overreliance")
LLM10	Unbounded Consumption	renomeado/ampliado (era LLM04 "Model DoS")
Saíram do Top 10 em 2025: Insecure Plugin Design e Model Theft (viraram parte de outras categorias).


A grande sacada: os 10 riscos mapeiam na cadeia da Aula 1
Lembra da cadeia modelo → orquestração → ferramentas → dados? Os 10 riscos não são uma lista solta — cada um vive numa parte da cadeia:

Onde, na cadeia	Riscos OWASP que moram ali
Entrada / contexto	LLM01 (injection), LLM06 (disclosure)
O modelo em si	LLM03 (poisoning), LLM04 (DoS), LLM10 (theft)
A saída	LLM02 (output handling), LLM09 (overreliance)
Ferramentas	LLM07 (plugin inseguro), LLM08 (excessive agency)
Terceiros / cadeia	LLM05 (supply chain)
🔑 Mensagem da Aula 2: o Top 10 te dá nome e endereço para cada risco. Em vez de "LLM é perigoso", você passa a dizer "meu agente tem risco de LLM08 porque a ferramenta de e-mail não pede confirmação" — e isso é acionável.

⚠️ Nota importante para você, autor (versão do OWASP)
A lista do CONTEXT.md é a do OWASP Top 10 for LLM Applications de 2023. O OWASP publicou uma revisão em 2025 que mudou nomes e ordem — vale você decidir qual ensinar no curso. As principais mudanças na versão 2025:

2023 (no seu CONTEXT)	2025 (atual)
LLM02 Insecure Output Handling	virou LLM05 Improper Output Handling
LLM06 Sensitive Info Disclosure	subiu para LLM02
LLM08 Excessive Agency	subiu para LLM06
LLM04 Model DoS	virou LLM10 Unbounded Consumption
LLM07/LLM10 (Plugin/Theft)	saíram do Top 10
—	novos: System Prompt Leakage, Vector & Embedding Weaknesses (riscos de RAG!), Misinformation
Não vou alterar o CONTEXT.md — só estou sinalizando, porque ensinar a versão de 2023 como "atual" pode datar o curso. Quer que eu prepare uma comparação detalhada 2023 × 2025 para você decidir? (Posso pesquisar as fontes oficiais antes de produzir qualquer material.)

✅ Checks de entendimento
Qual a diferença essencial entre LLM01 (Prompt Injection) e LLM02 (Insecure Output Handling) — um é sobre a entrada, o outro sobre o quê?
Um chatbot que só conversa (sem ferramentas, sem RAG) — quais dos 10 riscos praticamente não se aplicam a ele? (Dica: use a tabela da cadeia.)
Por que LLM08 (Excessive Agency) e LLM09 (Overreliance) são, no fundo, dois lados da mesma moeda — "confiar demais no modelo"?
Responde o que conseguir (ou "não sei, me diga") que eu fecho. E qual o próximo passo: aprofundar algum risco, decidir a questão 2023×2025, ou seguir para a Aula 3?



1. LLM01 (Prompt Injection) × LLM02 (Insecure Output Handling)
A diferença é onde o problema acontece no fluxo:

LLM01 — Prompt Injection = problema na ENTRADA. O atacante manipula o que entra no modelo para subvertê-lo. O alvo é o próprio modelo — fazê-lo desobedecer o desenvolvedor.
LLM02 — Insecure Output Handling = problema na SAÍDA. Aqui ninguém engana o modelo. O erro é a aplicação confiar cegamente no texto que SAI dele e jogá-lo em outro sistema (navegador, banco, shell) sem sanitizar. O alvo do dano é o sistema a jusante — vira XSS, SQL injection, RCE.
Em uma frase: LLM01 é "alguém mexeu no que entra no modelo"; LLM02 é "alguém confiou demais no que saiu do modelo".

🔗 E o pulo do gato: eles se encadeiam. Uma prompt injection (LLM01) faz o modelo gerar uma saída maliciosa (ex.: <script>), e o insecure output handling (LLM02) deixa essa saída causar estrago no navegador. Entrada compromete → saída executa.

(Na lista 2025 isso é LLM05 "Improper Output Handling" — mesmo conceito, só mudou o número.)

2. Chatbot que só conversa — quais riscos quase não se aplicam?
Usando a tabela da cadeia: se não há ferramentas e não há RAG, as camadas "ferramentas" e "dados externos" da cadeia somem — e os riscos que moram nelas vão junto:

LLM07 (Insecure Plugin Design) — não há plugins. ❌ não se aplica.
LLM08 (Excessive Agency) — não há ações nem autonomia; o pior que acontece é uma resposta ruim. ❌ não se aplica.
(Riscos específicos de RAG — na 2025, "Vector and Embedding Weaknesses" — também não se aplicam, pois não há base de recuperação.)
Mas atenção: a maioria dos riscos CONTINUA valendo, porque o chatbot ainda tem entrada, modelo, saída e cadeia de fornecimento:

LLM01 (injection na entrada), LLM06 (vazar system prompt / dados memorizados), LLM03 (modelo foi treinado), LLM04 (sobrecarga/custo), LLM05 (supply chain do modelo/libs), LLM09 (usuário confia na resposta), LLM10 (roubo do seu modelo).
LLM02 fica parcial: se a saída é só texto puro, o risco cai; se for renderizada como HTML/markdown, o XSS volta.
🔑 É a prova prática da frase da Aula 1: "a superfície de ataque é a cadeia inteira". Tire ferramentas e RAG da cadeia e os riscos daquelas peças desaparecem — o resto da cadeia continua exposto.

3. Por que LLM08 (Excessive Agency) e LLM09 (Overreliance) são dois lados da mesma moeda
Os dois nascem da mesma falha: tratar a saída do modelo — que é falível e alucina (Aula 1) — como se fosse confiável. A diferença é quem confia demais:

Quem confia demais	O que acontece
LLM08 Excessive Agency	o sistema	Dá ao modelo poder de agir sem checagem → ele executa ações no mundo real
LLM09 Overreliance	o humano	Aceita a resposta como verdade sem verificar → toma decisões erradas
Excessive Agency = a máquina confia demais → automatiza ações com base no que o modelo "decidiu".
Overreliance = a pessoa confia demais → usa a informação do modelo sem conferir.
E como a raiz é a mesma, a defesa é a mesma filosofia: não confiar cegamente. Para LLM08 → menor privilégio + confirmação humana antes de agir. Para LLM09 → revisão humana + verificação + citar fontes. Ambas reintroduzem o humano/checagem no ponto onde a confiança cega ia causar dano.

Resumindo a moeda: se quem confia demais é o sistema (e ele age), é LLM08; se quem confia demais é a pessoa (e ela acredita), é LLM09.

(Na 2025: Excessive Agency vira LLM06; Overreliance foi reformulada como LLM09 "Misinformation", focando no lado da informação falsa.)