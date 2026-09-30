# PPT_CONTEXT — Padrão dos slides do curso LLM Security

> **Fonte de verdade = texto.** Por aula: `aulaN/slides/aulaN_gamma.md` (slides).
> **Saída = Gamma.app** (tema Alura).
> Complementa `CONTEXT.md` (curso) e `PROJECT_CONTEXT.md` (lab CredSim).

---

## 1. Princípios
- **PT-BR**, didático, **sem matemática pesada**; **exemplos concretos**; termos consagrados em inglês (prompt injection, RAG…).
- **Segurança defensiva**: todo ataque vem com a mitigação. **OWASP sempre 2025.**
- **OWASP Top 10 = "documento padrão de conscientização"** (lista priorizada de riscos) — **nunca** chamar de "framework".

## 2. Vídeo e safe zone
- **Aula = módulo de 1h–1h20**, entregue em **vídeos curtos de 8–12 min** — **~8–9 teóricos + ~2–4 de prática (≈ 10–12 no total)**; um vídeo pode ir a ~25 min para não quebrar uma explicação importante. Cada vídeo é **autocontido** (micro-abertura "onde estamos" + fecho "no próximo vídeo"), com 3–5 bullets/slide (~40–60s cada).
- **Vídeos de prática são separados dos de teoria** (bloco à parte — ver §3).
- **Facecam (gravação):** retângulo no **canto inferior direito** — **302×192px (15,7%×17,8%), 32px da direita / 60px da base**. Nada crítico ali. Guia: `templates/tema-alura-gamma.md` §9.

## 3. Estrutura do deck
Deck **agrupado por vídeo** (marcadores `<!-- ═══ VÍDEO N … ═══ -->` no `.md`). Blocos:

| Bloco | O que entra | Vídeos |
|---|---|---|
| teórico | abertura/agenda + tópicos da ementa (**1 tópico ≈ 1 vídeo**), cada um com gancho de segurança (marcador **Segurança:**) | ~8–9 |
| **prático** *(separado)* | **um exemplo por vídeo**: objetivo → passos → o que observar/lição; roda no notebook e/ou no **CredSim** (negativo/vulnerável + positivo/mitigado) | ~2–4 |
| conclusão | síntese + gancho para a próxima aula | 1 |

> **Vídeos de prática ficam num bloco à parte, separados do teórico** (mesmo arquivo, marcados; `secao=prática`).
> **Abertura do curso = `aula0/slides/`** — **boas-vindas** (capa do professor + objetivos + estrutura das 6 aulas + como aprender/lab): **1 vídeo curto, sem diagramas**. Substituiu a antiga `introducao/`.

## 4. Arquivos por aula
`aulaN/slides/aulaN_gamma.md` (texto dos slides, slides separados por `---`, **agrupados por vídeo** via comentários `<!-- ═══ VÍDEO N … ═══ -->`).

## 5. Formato do `.md` (para o Gamma)
- 1º bloco: `#` título da aula + bullets de capa. Cada slide: `---`, `## título`, a **seção** em itálico (`_conteúdo_`) e os bullets.
- **Bullet:** `- **rótulo** — descrição`. Rótulo = 1–2 palavras; **a descrição traz o EXEMPLO concreto**. Ganchos de segurança prefixados com o **marcador textual `Segurança:`**.
- **Sem caracteres de imagem (emoji)** no texto dos slides — nada de cadeado, pause etc.; use o marcador textual `Segurança:` no lugar. Símbolos tipográficos (×, ≠, →, ·, —) são permitidos.
- **Diagrama/layout = elemento NATIVO do Gamma**: **tabela** → comparação; **lista numerada** → steps/escada; **diagrama de blocos** montado no Gamma. **Nunca usar ASCII** (o Gamma não entende) nem deixar o diagrama só em comentário — descreva o alvo no comentário `LAYOUT` e monte o nativo no Gamma.
- **Roteiro/embasamento** rico vai num comentário `<!-- LAYOUT … / ROTEIRO … -->` no `.md` (o Gamma ignora comentários na importação): `LAYOUT` = como montar o slide; `ROTEIRO` = como abordar o assunto.
- **Uma view por slide**; **sem forward-reference** (só referências para trás, como reforço).

## 6. Gamma.app — montagem
1. **Create new → Paste in text** com o `aulaN_gamma.md`; modo **"preservar texto"**; tema **Alura**; **imagens = None**.
2. Aplicar fundos/safe zone e transformar os blocos de layout em diagramas **nativos** do Gamma. Tema, assets e procedimento: **`templates/tema-alura-gamma.md`**.

## 7. Checklist por aula
- [ ] Bloco **teórico** (abertura + tópicos + conclusão) e bloco **prático separado**; cada tópico com gancho de segurança (**Segurança:**) + exemplo.
- [ ] Prática: **um exemplo por vídeo**, referenciando o notebook e/ou a CredSim (negativo + positivo).
- [ ] Diagramas **nativos do Gamma (sem ASCII)**; **sem emoji no texto** (marcador textual `Segurança:`); safe zone da facecam respeitada.
- [ ] OWASP **2025**; sem "framework"; sem forward-reference.

## 8. Rota `.pptx` (descontinuada)
`gerar_pptx_alura.py` gera `.pptx` no modelo `templates/ALURA MODELO NOVO SLIDE.pptx` (duplicando slides-modelo). **Não está em uso** — os decks vão pelo **Gamma**. Um `.pptx` de exemplo permanece em `templates/` (ex.: `Aula-1-Como-LLMs-Funcionam.pptx`). Mantidos o **modelo** Alura, os assets e o gerador, caso a rota seja retomada.
