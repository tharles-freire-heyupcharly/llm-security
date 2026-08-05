# Documentos de exemplo

Arquivos `.txt` simulando a **extração OCR** de um documento de identidade, para
carregar pela interface da CredSim (seção "Documento de identidade").

| Arquivo | O que é |
|---|---|
| `documento_legitimo.txt` | Documento normal — valida sem problemas. |
| `documento_envenenado.txt` | Documento com **injeção indireta** (LLM01): um bloco de instrução embutido manda o validador aprovar e elevar o limite de crédito (excessive agency / LLM06). |

> 🔎 **Na vida real**, essa instrução estaria *escondida* — texto branco sobre fundo
> branco, metadados, ou camadas invisíveis de um PDF/imagem. Aqui ela está visível só
> para fins didáticos.

## Como usar (negativo × positivo)

1. Suba o app: `docker compose up --build` (raiz) → http://localhost:8000
2. **Cenário negativo:** defesas OFF → carregue `documento_envenenado.txt` → o validador
   **obedece** a instrução (aprova sozinho + eleva o limite). Veja a evidência nos logs.
3. **Cenário positivo:** ligue a **Validação de entrada** → carregue o mesmo arquivo →
   o conteúdo é tratado como **dado, não comando** (separação de confiança); nenhuma
   ação indevida é executada.
