# ROTEIRO_FALADO_CONTEXT — Padrão do roteiro falado (teleprompter)

> Guia para construir o **roteiro falado** de cada aula — a fala do professor, slide a slide, para gravar os vídeos.
> Complementa `PPT_CONTEXT.md` (slides/Gamma) e `CONTEXT.md` (curso).
> **Motivo:** o professor travou na hora de gravar; o roteiro falado é o trilho para ele nunca ficar sem o próximo passo.

---

## 1. O que é / fonte
- Um `.md` por aula com a **fala pronta** (1ª pessoa, dirigida à turma) de cada slide.
- **Fonte:** deriva do comentário `<!-- ROTEIRO … -->` do `aulaN/slides/aulaN_gamma.md` (o "o que falar e como"), transformado em fala natural — mais os exemplos concretos dos bullets.
- **Não** substitui os slides; é material de apoio para gravação.

## 2. Arquivo por aula
- Caminho: `aulaN/recursos/aulaN_roteiro_falado.md`.
- **Feito:** aula 1 (`aula1/recursos/aula1_roteiro_falado.md`). **Pendentes:** aulas 2–6, mesmo padrão.
- Formato:
  - Cabeçalho curto ("O que é" + "Como usar").
  - `## VÍDEO N · título · ~X min` — espelha os marcadores `<!-- ═══ VÍDEO N … -->` do `aulaN_gamma.md`.
  - `**Slide — <título do slide>**` e, abaixo, a fala em citação (`>`).
  - Uma fala por slide (~40–60s). `[pausa]` onde respirar.

## 3. Perfil de estilo (voz REAL do professor — calibrado no treino_limpo.txt)
- **Registro explicativo e caloroso, mas neutro** (sem gírias). Voz calma. Frases podem ser mais longas e discursivas — é a cadência natural dele.
- **Tratamento:** mistura natural — **"vamos"** (nós inclusivo) para a jornada ("vamos falar", "vamos ver"); **"eu/vou"** ao enquadrar ("vou abordar", "eu tenho o código"); **"vocês"** ocasional (ex.: "bem-vindos", "vocês pedem").
- **Conectores naturais dele — USAR (NÃO são muletas):** "Vamos falar sobre…", "Falando de…", "Começando por…", "Com isso…", "Novamente falando de…".
- **"Né?"** faz parte da fala dele — permitido, com moderação (~1–3 por vídeo).
- **Explicar siglas em português na 1ª vez** (LLM = Large Language Models; RLHF = reforço por feedback humano).
- **Termos técnicos em inglês, ditos em inglês** (prompt injection, RAG, guardrails, prepared statement, read-only, excessive agency, stateless, backdoor…).
- **Metáforas do curso** (o sorteio com pesos × a calculadora; o consultor com amnésia; o leitor voraz; o roteiro de teatro; a "parede" do prepared statement) — usar **uma vez**, sem floreio. **Evitar metáforas que estereotipem profissões** (ex.: comparar o modelo a um estagiário que "só estima", sugerindo que estagiários são pouco confiáveis).
- **Referência de voz:** `aula1/recursos/treino_limpo.txt` — transcrição real do professor (limpa) é o modelo de cadência.

## 4. Abertura (capa) — modelo aprovado (voz do professor)
> Olá. Bem-vindos à [primeira/segunda/…] aula do curso de LLM Security. Esta aula apresenta os conceitos importantes sobre [tema] — [sigla expandida na 1ª vez]. [Uma frase do que vamos ver / no nível necessário para avaliar segurança, sem matemática.] Vamos começar.

## 5. Estrutura de cada slide (o trilho)
Situar (1 frase) → afirmação (o conceito) → **exemplo concreto** → lição/gancho curto.
O exemplo é a âncora: **internalizar o exemplo, não decorar as palavras**.

## 6. O que ainda evitar (mesmo na voz explicativa)
- **Editorializar** em vez de mostrar: "a resposta surpreende", "é um insight central", "um dos pontos mais importantes".
- **Direção de palco vazando na fala:** "com firmeza aqui", "deixem o peso assentar", "pesem bem este".
- **Repetição vazia** e conectores empilhados sem conteúdo.
- **Erros de transcrição (STT) — sempre revisar:** ex.: "RAG" vira "rádio", "paráfrases" vira "para frases", "maneira" vira "madeira", "open source" vira "opensors".
> Obs.: "Vamos falar sobre…", "Falando de…" e "né?" (moderado) **não** são muletas aqui — são a voz do professor (ver §3).

## 7. Como o professor usa (grava)
- **Grave slide a slide** (~40–60s). Vídeo gravado perdoa: refaça sem medo.
- **`[pausa]` = respire.** Silêncio é editável.
- **Internalize o exemplo, não as palavras.**
- **Travou? Recomece a frase** — corta na edição.

## 8. Edição colaborativa (importante)
- O professor **edita o `.md` à mão**. **Antes de reescrever, releia o arquivo e preserve as edições dele** — nunca sobrescrever cegamente.
- Se ele estiver editando ao vivo (o Write colide), entregar a versão enxuta em **arquivo separado** (`aulaN_roteiro_falado_enxuto.md`) ou como **lista de cortes**, sem tocar no arquivo que ele está mexendo.

---
Relacionado: `PPT_CONTEXT.md` (slides), `CONTEXT.md` (curso). Memória: `project-roteiro-falado`.
