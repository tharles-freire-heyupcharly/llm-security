# LLM Security: Riscos em Modelos de Linguagem

- **Tharles Freire** — gerente de DevSecOps e SRE · professor de Cloud Security e DevSecOps na FIAP · mestre em Computação Aplicada (Mackenzie).
- **Trilha LLM Security · Curso 1** — riscos em modelos de linguagem.

<!--
LAYOUT: capa — título grande + subtítulo; tema Alura, accent #1F53E5; imagens = None. Nada crítico no canto inferior direito (safe zone da facecam).
ROTEIRO: boas-vindas ao curso. Apresente-se — Tharles Freire, gerente de DevSecOps e SRE, professor de Cloud Security e DevSecOps na FIAP e mestre em Computação Aplicada pelo Mackenzie. Situe: este é o Curso 1 da trilha LLM Security, a aula-alicerce que dá vocabulário e o mapa de ameaças para toda a trilha. Este é um vídeo curto de boas-vindas; o conteúdo começa na Aula 1.
-->

---

## O que você vai aprender
_introdução_

<!--
LAYOUT: lista de objetivos, um ícone por item; accent #1F53E5. Sem diagrama.
ROTEIRO: os objetivos de aprendizagem do curso, em bloco. Prometa o resultado: ao final você terá vocabulário + mapa de ameaças + método para AVALIAR risco. Tom: desmistificar, não assustar.
-->

- **Como o LLM funciona** — no nível necessário para avaliar risco, sem matemática pesada.
- **Superfícies de ataque** — onde sistemas com LLM quebram em ambientes corporativos.
- **OWASP Top 10 (2025)** — a referência de risco para aplicações de LLM.
- **Mitigações e avaliação** — defender em camadas e avaliar a postura de uma aplicação.

---

## Estrutura do curso
_introdução_

<!--
LAYOUT: roadmap/timeline das 6 aulas; accent #1F53E5.
ROTEIRO: o mapa do curso, uma frase por aula. Aula 1 — como LLMs funcionam (tokens, geração, contexto, treino), sem matemática pesada. Aula 2 — OWASP Top 10 para LLMs 2025, o documento padrão de conscientização que dá 'nome e endereço' a cada risco. Aulas 3 a 5 — superfícies de ataque por arquitetura, riscos de dados e privacidade (LGPD), e mitigações em camadas. Aula 6 — juntar tudo num método para AVALIAR uma aplicação, com threat modeling e o laboratório.
-->

- **Como LLMs funcionam (Aula 1)** — no nível necessário para avaliar risco de segurança.
- **OWASP Top 10 para LLMs / 2025 (Aula 2)** — documento padrão de conscientização sobre os principais riscos.
- **Superfícies, dados e mitigações (Aulas 3–5)** — onde os sistemas quebram e como blindar.
- **Avaliar uma aplicação (Aula 6)** — threat modeling + laboratório.

---

## Como vamos aprender
_introdução_

<!--
LAYOUT: 3 bullets; destaque o lab CredSim. Accent #1F53E5.
ROTEIRO: como o curso está organizado. Segurança defensiva — cada risco vem com a mitigação correspondente. A prática acontece no CredSim, uma plataforma de crédito fictícia em Docker, onde você ataca e depois defende, com evidência nos logs. Deixe o objetivo claro: AVALIAR risco em sistemas com LLM, não 'hackear'. Feche as boas-vindas e mande para a Aula 1.
-->

- **Do risco à ação** — cada risco vem com a mitigação correspondente (segurança defensiva).
- **Lab CredSim** — uma plataforma de crédito fictícia (Docker) onde você ataca e defende.
- **O objetivo** — AVALIAR risco em sistemas com LLM, não "hackear".
