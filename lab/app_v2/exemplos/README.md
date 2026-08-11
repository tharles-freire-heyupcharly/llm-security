# Documentos de exemplo (v2)

PDFs de verdade — a interface faz upload real de `.pdf` e o backend extrai o
texto no servidor (`labcore/pdf_utils.py`, via `pypdf`) antes de validar.
Gerados por `scripts/gerar_documentos_exemplo.py` (roda de novo se o texto
mudar). Não confundir com `lab/exemplos/*.txt`, usados pela v1 e pelos
notebooks — são específicos desta v2.

| Arquivo | O que é |
|---|---|
| `documento_legitimo.pdf` | Documento normal — valida sem problemas. |
| `documento_envenenado.pdf` | Documento com **injeção indireta** (LLM01): um bloco de instrução embutido no texto manda o validador aprovar e elevar o limite de crédito (excessive agency / LLM06). |

> **Na vida real**, essa instrução estaria *escondida* — texto branco sobre
> fundo branco, metadados, ou camadas invisíveis do PDF. Aqui ela está visível
> no texto extraído só para fins didáticos.

## Como usar (negativo × positivo)

1. Suba o app v2: `docker compose up --build` (raiz) → http://localhost:8010
2. **Cenário negativo:** defesas OFF → carregue `documento_envenenado.pdf` na
   seção "Documento de identidade" → o validador **obedece** a instrução
   (aprova sozinho + eleva o limite). Veja a evidência nos logs (`/api/logs`).
3. **Cenário positivo:** ligue a **Validação de entrada** → carregue o mesmo
   arquivo → o conteúdo é tratado como **dado, não comando** (separação de
   confiança); nenhuma ação indevida é executada.
