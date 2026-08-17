CLAUDE.md — Contexto do Projeto

Este arquivo orienta o Claude Code ao trabalhar neste repositório. Leia-o por completo antes de qualquer tarefa.


O que é este repositório

Material didático do curso "LLM Security: Riscos em Modelos de Linguagem", produzido para a plataforma Alura (cursos em vídeo, formato pré-gravado).

Este é o primeiro curso de uma trilha de segurança em sistemas de IA. O tom deve ser introdutório, didático e objetivo — o aluno está aprendendo o assunto agora, do zero. Não assuma conhecimento prévio de segurança em IA.


Enunciado oficial do curso

Trilha: LLM Security · Curso 1: LLM Security: riscos em modelos de linguagem.

Texto completo do enunciado recebido em `EMENTA.md` (não reescrever). Resumo: mapear como LLMs funcionam do ponto de vista de segurança, as superfícies de ataque que introduzem, como o OWASP Top 10 para LLMs organiza esses riscos e as estratégias de mitigação por categoria — o curso que dá vocabulário, estrutura e contexto para toda a trilha.


Papel do autor

O autor é o professor especialista do curso: prepara o material do curso e ministra as aulas. O Claude o apoia na preparação desse conteúdo.


Papel esperado do Claude

Você está atuando como assistente de produção de conteúdo educacional. As tarefas envolvem:


Criar e editar slides das aulas (Markdown para o Gamma: aulaN_gamma.md)
Criar e editar o material da parte prática (código de exemplo)
Organizar arquivos por aula (um diretório por aula, na main)
Escrever textos didáticos, roteiros e recursos de apoio


Sempre que houver dúvida de escopo, pergunte antes de produzir em vez de assumir.


Estrutura do repositório

llm-security/
├── CONTEXT.md           # Este arquivo (contexto do projeto / CLAUDE.md)
├── PPT_CONTEXT.md       # Padrão dos slides (Gamma): aulaN_gamma.md
├── PROJECT_CONTEXT.md   # Contexto do lab prático (app CredSim)
├── ROTEIRO_FALADO_CONTEXT.md  # Padrão do roteiro falado (teleprompter) por aula
├── EMENTA.md            # Enunciado oficial recebido (OWASP antigo — não reescrever)
├── introducao.md        # Descritivo geral do curso (visão do aluno) — stub
├── NOTAS*.md            # Notas de estudo / anotações do autor (não editar)
├── README.md            # Readme do repositório
├── templates/           # Tema Alura (tema-alura-gamma.md), modelo .pptx e assets
├── aula0/
│   └── slides/          # Boas-vindas do curso (aula0_gamma.md)
├── aula1/
│   ├── slides/          # aulaN_gamma.md (slides Gamma)
│   ├── pratica/         # Notebooks Jupyter da aula
│   └── recursos/        # Links, referências, material de apoio (inclui roteiro falado)
├── aula2/ … aula6/      # (mesma estrutura de slides/pratica/recursos)
└── lab/                 # Laboratório prático
    ├── app/             # Plataforma CredSim v1: backend FastAPI, labcore, frontend
    ├── app_v2/          # Plataforma CredSim v2: motor de IA real (mock/local/real, Ollama) — ver PROJECT_CONTEXT.md
    └── aula1/ … aula6/  # README + notebooks de ataque/defesa por aula

Organização do trabalho


O repositório é privado.
Todo o conteúdo é desenvolvido na branch main — um diretório por aula (aula0 a aula6) mais o lab/ (app CredSim). Não há branches por aula.
A main mantém tudo: CONTEXT.md, os demais docs de contexto, a estrutura das aulas e o lab/.
Confirme que está na main antes de criar arquivos.



Formato das aulas


6 aulas no total.
Cada aula é um módulo de 1h a 1h20, entregue em vídeos curtos de 8 a 12 minutos (um vídeo pode chegar a ~25 min para não quebrar uma explicação importante) — cerca de 10 a 12 vídeos por aula (~8–9 teóricos + 2–4 de prática). Os vídeos de prática ficam num bloco separado dos de teoria.
Cada aula entrega: slides + material prático.
Linguagem dos exemplos práticos: Python (notebook Jupyter + a app CredSim em Python/FastAPI).



Ementa do curso

6 aulas — tópicos e objetivos de aprendizagem completos em `EMENTA.md` (não reescrever). O conteúdo/slides seguem essa estrutura à risca, com uma única divergência consciente:

Nota sobre versões do OWASP (Aula 2). O enunciado oficial (EMENTA.md) reproduz a versão antiga do OWASP Top 10 para LLMs (ex.: LLM02 Insecure Output Handling, LLM04 Model DoS, LLM05 Supply Chain Vulnerabilities, Insecure Plugin Design, Overreliance, Model Theft). O curso e os slides usam sempre o OWASP Top 10 for LLMs 2025:
- LLM01 Prompt Injection · LLM02 Sensitive Information Disclosure · LLM03 Supply Chain · LLM04 Data and Model Poisoning · LLM05 Improper Output Handling
- LLM06 Excessive Agency · LLM07 System Prompt Leakage · LLM08 Vector and Embedding Weaknesses · LLM09 Misinformation · LLM10 Unbounded Consumption
O texto oficial da ementa não deve ser reescrito — ementa = enunciado oficial recebido; slides/conteúdo = versão 2025 atual.



Diretrizes de conteúdo


Didático antes de exaustivo. É um curso de entrada. Prefira clareza a profundidade excessiva.
Exemplos concretos. A Alura valoriza exemplos práticos ao longo das aulas. Use casos reais quando possível.
Sem matemática pesada. O público é técnico, mas o foco é segurança, não machine learning teórico.
Português do Brasil. Termos técnicos consagrados (prompt injection, RAG, guardrails) podem ficar em inglês.
Segurança defensiva. O material ensina a identificar e mitigar riscos. Demonstrações de ataque servem ao entendimento defensivo e devem vir acompanhadas da mitigação correspondente.
OWASP sempre 2025. Slides e conteúdo usam a lista OWASP Top 10 for LLMs 2025 (ver nota na Aula 2 da ementa). Nos slides, nunca chamar o OWASP Top 10 de "framework" — é um documento de conscientização; a palavra "framework" só é aceitável no texto oficial da ementa.
Sem emoji nos slides. O texto dos slides (títulos e bullets) e os notebooks não usam caracteres de imagem (emoji). Ganchos de segurança usam o marcador textual "Segurança:" no lugar do cadeado. Símbolos tipográficos (×, ≠, →, ·) são permitidos. Detalhes de formato em PPT_CONTEXT.md.



Convenções de trabalho


Confirme que está na branch main antes de criar arquivos.
Não avance para outras aulas sem o autor pedir.
Antes de gerar código prático, confirme a linguagem e as dependências.
Mantenha o introducao.md como o documento de visão do aluno; mudanças estruturais relevantes devem ser refletidas nele.
Nunca modifique arquivos de notas (NOTAS.md, NOTAS1.md e quaisquer NOTAS*.md / anotações do autor) sem ordem expressa do autor. São documentos pessoais de estudo; o Claude só os edita mediante pedido explícito — nem deve propor edição automática deles.
Faça commits pequenos e descritivos, em português, descrevendo o que foi produzido (ex.: aula1: adiciona slides de introdução a transformers).
Abra sempre novas solicitações em threads/agentes diferentes: quando houver várias solicitações independentes (ex.: lista de itens a verificar/implementar), trate cada uma em paralelo (Agent tool), não sequencialmente na mesma linha de raciocínio. Testes de backend e de frontend rodam sempre em thread própria, nunca um atrás do outro no mesmo comando.