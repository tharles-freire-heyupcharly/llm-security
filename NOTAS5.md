Aula 5 — Mitigações e controles de segurança para LLMs
1. Defesa em profundidade — o princípio guarda-chuva
O que é: como nenhum controle isolado barra prompt injection (já estabelecemos: não tem "conserto" definitivo), você empilha várias camadas imperfeitas. Se uma falha, a próxima segura. É o conceito clássico de segurança, aplicado ao LLM.

As camadas, mapeadas na cadeia (Aula 1):


entrada → [validação/guardrail de entrada] → system prompt blindado →
MODELO → [validação/guardrail de saída] → [ferramentas com menor privilégio
+ human-in-the-loop] → ação/resposta
                  ↑ monitoramento cobrindo tudo ↑
A mentalidade: o modelo é o elo não-confiável no meio. Você não tenta torná-lo perfeito — você limita o raio de explosão quando ele falhar. Os 5 tópicos seguintes são as camadas dessa figura.

2. Input validation e sanitização de prompts
O que é: validar e limpar o que entra no modelo.

⚠️ Honestidade primeiro: como vimos na Aula 1 (filtro de palavra-chave é fraco), você não consegue validar 100% a intenção de linguagem natural. Então isto é uma camada fina e útil — nunca a defesa principal.

Técnicas:

Limites de tamanho/formato; rejeitar input malformado.
Separar confiável de não-confiável: delimitar claramente o conteúdo do usuário/RAG (usar os roles da API — system × user), instruindo o modelo a tratá-lo como dado, não comando.
Allowlist quando o domínio permite (constranger a entradas esperadas).
Um classificador/LLM auxiliar que rastreia tentativas de injeção.
Sanitizar dados antes de indexar no RAG (ataca LLM08).
Mitiga: LLM01 (parcial), LLM08.

3. Output validation
O que é: validar o que sai do modelo antes de usar. Tratar a saída como input não-confiável (LLM05).

🔑 Costuma ser mais confiável que a validação de entrada, porque você checa contra um formato esperado conhecido — é mais fácil verificar "isso é um JSON válido?" do que "essa frase é maliciosa?".

Técnicas:

Validação de schema/formato (espera JSON? valide).
Encodar/sanitizar antes de renderizar (mata o XSS); parametrizar antes do SQL; nunca eval.
Filtro de egress / varredura de PII e segredos na saída → bloqueia a exfiltração via imagem-markdown que vimos na Aula 4.
Grounding/verificação de afirmações (combate LLM09).
Mitiga: LLM05, LLM02, LLM09.

4. Princípio do menor privilégio para agentes
O que é: o controle mais importante para sistemas de alto impacto. Já que você não confia no modelo, limite o que ele PODE fazer. É a materialização do "limitar o raio de explosão".

Técnicas:

Dar às ferramentas a permissão mínima (read-only quando possível; credenciais com escopo apertado).
Reduzir quais ferramentas existem — não conecte o que não precisa.
Human-in-the-loop / confirmação para ações irreversíveis ou de alto impacto (transferir dinheiro, apagar, enviar e-mail externo).
Credenciais efêmeras e por sessão; sandbox para execução de código.
Nunca dar acesso amplo permanente (ex.: banco de produção com escrita).
Mitiga: LLM06 (excessive agency) — defesa primária. E contém o estrago de uma LLM01 bem-sucedida.

🔑 A regra de ouro: mesmo que a injeção engane o modelo, se a ferramenta não tem poder de causar dano grave (ou exige sua confirmação), o ataque morre aí.

5. Guardrails
O que é: uma camada de política dedicada ao redor do modelo, que aplica regras de segurança/conteúdo. Existem guardrails de entrada (bloquear tópicos proibidos, injeção, PII) e de saída (bloquear resposta tóxica, vazamento, fora de escopo). Podem ser baseados em regras, classificadores ou um LLM-juiz separado. (Ex. de ferramentas: NeMo Guardrails, Llama Guard.) 🔎

Como encaixa: é a camada programável entre usuário↔modelo e modelo↔saída — operacionaliza os tópicos 2 e 3 com políticas explícitas.

Mitiga: transversal — LLM01, LLM02, LLM06 (restrição de tópico/ação), LLM09.

⚠️ Limitação: guardrails também são imperfeitos (se forem baseados em LLM, são probabilísticos e burláveis). São uma camada, não bala de prata. Nunca deixe o guardrail ser seu único controle.

6. Monitoramento de sistemas de LLM em produção
O que é: como você não previne tudo, precisa detectar e responder. É observabilidade aplicada a LLM.

O que monitorar:

Logs de prompts/respostas — com cuidado de privacidade (não logar segredos/PII de forma descuidada; isso seria criar um novo vazamento).
Anomalias: picos de uso/custo (LLM10 — denial of wallet/extração), chamadas de ferramenta incomuns, padrões de jailbreak/injeção.
Flags na saída: vazamento de PII, violação de política.
Loops de feedback: denúncias de usuários, red-teaming periódico.
Métricas: taxa de recusa, latência, consumo de tokens.
Mitiga: detecção transversal — especialmente LLM10, e pegar LLM01/LLM06 em ação. Alimenta resposta a incidentes e melhoria contínua.

A história da Aula 5 (síntese)
Cada controle pega uma parte — juntos formam a defesa em profundidade:

Camada	Onde atua	Riscos que mitiga (2025)
Input validation	entrada	LLM01 (parcial), LLM08
Output validation	saída	LLM05, LLM02, LLM09
Menor privilégio	ferramentas	LLM06 + contém LLM01
Guardrails	entrada e saída	LLM01, LLM02, LLM06, LLM09
Monitoramento	tudo	LLM10 + detecção geral
🔑 A grande mensagem: não existe controle único que resolva. A segurança de LLM é camadas imperfeitas + menor privilégio + detecção, tudo guiado por uma premissa: o modelo vai falhar; seu trabalho é conter a falha.

✅ Checks de entendimento
Por que output validation costuma ser mais confiável do que input validation contra os riscos de LLM? (Dica: verificar formato esperado × adivinhar intenção.)
Se você só pudesse implementar UM controle num agente que mexe com banco de produção, qual escolheria e por quê? (Dica: raio de explosão.)
Por que guardrails sozinhos não bastam — e a que princípio da aula isso remete? (Dica: tópico 1.)
Responde o que quiser (ou "não sei, me diga"). Depois fechamos a trilha com a Aula 6 (avaliando a segurança de uma aplicação de LLM), que junta tudo num método de avaliação + threat modeling + o laboratório final.