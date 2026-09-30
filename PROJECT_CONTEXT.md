# PROJECT_CONTEXT — Laboratório prático do curso LLM Security

> Documento de contexto do **projeto prático** do curso "LLM Security: Riscos em Modelos de Linguagem" (Alura).
> Complementa o `CONTEXT.md` (que descreve o curso). É a **fonte de verdade** das decisões do projeto da aplicação prática.
> **Status (jul/2026):** stack decidida (FastAPI + frontend web leve, Docker). **Slides + roteiros das 6 aulas prontos** (padrão Gamma; ver `PPT_CONTEXT.md`). **App em `lab/app` (v1) completo com as 6 superfícies**: `chatbot` (+ XSS), `documento` (agente + injeção indireta), `rag` (envenenamento + vazamento entre tenants), `analise` (agente/pipeline de código — SQL gerado e executado), `negociacao` (multi-agent — Agente Pesquisador → Agente Negociador), `api_exposta` (IDOR + rate limit), além de `credit` (produto, não-LLM). 4 toggles de defesa (`input_validation`, `output_validation`, `least_privilege`, `api_security`), cobertos por testes automatizados (`lab/app/tests/`, `pytest`, 44 testes). **Notebooks completos e testados** (rodam ponta a ponta contra o app real, `docker compose up` + `TENANT_ID=financeira-A`): `aula1/pratica/aula1_demos.ipynb`, `aula2/pratica/owasp_tour.ipynb`, `lab/aula3/01_chatbot.ipynb`–`06_api_exposta.ipynb`, `lab/aula4/privacidade_lgpd.ipynb`, `lab/aula5/defesas.ipynb`, `lab/aula6/checklist_avaliacao.ipynb` + `relatorio_modelo.md`. Pendente: revisão editorial dos slides/roteiro à luz do app final (checar se algum "NOVO SLIDE" ainda precisa ser colado no Gamma) e o `.pptx`/vídeo em si — fora do escopo deste lab.
>
> **Status (ago/2026):** em construção `lab/app_v2` — CredSim v2, código próprio separado do v1 (que segue intacto como referência/backup). Mesmas superfícies/toggles, mais motor de IA em 3 modos (`mock`/`local`/`real`), com `local` rodando um modelo open-source de verdade via Ollama e toggle do motor na própria UI. Detalhe técnico completo: `lab/app_v2/README.md` (não duplicado aqui).

---

## 1. Objetivo

Construir o material prático que demonstra, de forma **dinâmica e aplicada**, o conteúdo das 6 aulas — ataques e mitigações de segurança em LLMs. Serve como exemplo ao longo das aulas e como objeto do **laboratório da Aula 6**.

## 2. Abordagem (DECIDIDA)

Abordagem **combinada e em paralelo**:

- **LAB vivo** — uma aplicação com **interface gráfica** que cobre todas as superfícies de ataque, com **chave on/off** para demonstrar o problema (modo vulnerável) e a construção da defesa (modo mitigado).
- **Notebooks Jupyter** — em paralelo à app, organizados por cenário/aula, para exemplificar e seguir cada caso de forma **independente**. Os notebooks têm **métodos para testar e corrigir** comportamentos/erros da aplicação (atuam como harness de exploração e verificação).
- **Aula 6** — finaliza com um **notebook de checklist**: avaliação estruturada (framework + STRIDE adaptado + checklist por componente + matriz de risco + resumo executivo) aplicada sobre a própria app do lab.

## 3. Motor de LLM (DECIDIDO)

- **Mock + Real**, com **switch por configuração**.
- **Mock (padrão para gravação):** determinístico, sem chave nem custo — ataques sempre reproduzíveis no vídeo.
- **Real (opcional):** via API (Anthropic/Claude por padrão) ou modelo local. Chaves **somente via variável de ambiente**, nunca no código/repo.

## 4. Superfícies de ataque a cobrir (DECIDIDO)

A GUI deve cobrir as 6 superfícies da Aula 3:

1. Chatbot
2. RAG
3. Agentes com ferramentas
4. Multi-agent systems
5. LLMs em pipelines de código
6. APIs de LLM expostas

### Mapa superfície → aula → OWASP 2025
| Superfície | Aulas | Riscos OWASP 2025 |
|---|---|---|
| Chatbot | 1, 3 | LLM01, LLM07, LLM02, LLM05 |
| RAG | 3, 4 | LLM08, LLM01, LLM02 |
| Agentes | 3 | LLM06, LLM01, LLM05 |
| Multi-agent | 3 | LLM06 (propagado), LLM01 |
| Pipelines de código | 3 | LLM09, LLM05 |
| APIs expostas | 3 | LLM10, LLM02 |

## 5. Conceito e arquitetura da aplicação (DECIDIDO)

**Conceito:** uma plataforma fictícia de **originação de empréstimos com IA**. O cliente solicita um empréstimo via chat; a plataforma cadastra os dados, analisa risco com agentes, valida documentos, integra fornecedores de crédito e notifica por e-mail. O domínio (dinheiro + PII + LGPD) torna os riscos viscerais e dá uma narrativa única que cobre todas as superfícies.

**Funcionalidades × superfície × riscos:**
| Funcionalidade | Superfície | OWASP 2025 |
|---|---|---|
| Chat de solicitação (coleta dados do cliente/empréstimo) | Chatbot | LLM01, LLM07, LLM02 |
| Cadastro em base de clientes/empréstimos | (dado sensível) | LLM02 / Aula 4 |
| Suporte com recuperação de documentação | RAG | LLM08, LLM01, LLM02 |
| Agente de análise **gera e executa SQL/Python** | Agentes + Pipeline de código | LLM06, LLM05 |
| Agente valida documentos enviados pelo cliente | Agente + injeção indireta | LLM01 (indireta), LLM06 |
| Fluxo multi-agente: perfil/risco → **negocia taxa com fornecedor** | Multi-agent | LLM06 propagado, LLM01 |
| Notificações por e-mail (progresso/ofertas) | Agente (ferramenta de ação) | LLM06 |
| Integração com APIs de fornecedores de crédito | Egress/tools | Aula 4 (dados a terceiros), LLM03 |
| API REST do backend (auth/authz/rate-limit) | APIs de LLM expostas | LLM10, LLM02 |

**Arquitetura (núcleo compartilhado):**
- **`labcore/` (pacote Python):** cliente de LLM com switch mock/real, os cenários, as defesas (toggles) e o logging.
- **Backend FastAPI:** expõe os endpoints — é, ele mesmo, a superfície "API exposta" e o alvo dos notebooks; auth/authz/rate-limit demonstráveis.
- **Frontend web leve:** a interface gráfica da plataforma, com **toggle on/off (vulnerável ↔ mitigado)** por cenário e painel de logs.
- **Notebooks Jupyter:** consomem o `labcore`/a API para atacar, alternar defesas e testar/corrigir.
- **Docker:** roda como app web; **múltiplas instâncias = múltiplos "tenants/financeiras"** (demos de vazamento entre tenants). Parâmetros via variáveis de ambiente.

## 6. Princípios do cenário prático (guia de construção)

- **Defensivo:** todo ataque acompanha a mitigação; contraste **OFF → ON** é o momento didático.
- **Amarração tripla:** cada cenário ligado a um componente (Aula 1), um risco OWASP 2025 (Aula 2) e um controle (Aula 5).
- **Caber em 8–12 min** por aula; uma ideia por demo; tom introdutório; PT-BR.
- **Reprodutibilidade:** gravar no **mock** (LLM real é não-determinístico); versões de dependências fixas; setup mínimo; multiplataforma.
- **Segurança/ética:** tudo em sandbox/fictício; ferramentas "perigosas" simuladas; dados sintéticos (zero PII real); uso educacional explícito.
- **Estrutura:** README por aula; switch mock/real documentado; logs visíveis (alimentam Aulas 5 e 6).

## 7. Decisões em aberto / fechadas

- [x] Onde mora: pasta `lab/` na raiz, na branch **main**.
- [x] Nome da financeira fictícia: **CredSim**.
- [x] Primeiro build: **fatia vertical do Chatbot de solicitação** (Aula 1/3).
- [x] Detalhe do frontend web leve: **HTML + fetch**, sem framework — suficiente para as 6 superfícies; HTMX/React não se mostraram necessários.
- [x] As 6 superfícies implementadas e testadas (`lab/app/labcore/scenarios/` + `lab/app/tests/`).

## 8. Decisões registradas nesta rodada

- Pipeline de código → o **agente de análise gera e executa SQL/Python** sobre os dados do cliente.
- Multi-agent → agentes **montam perfil/risco do cliente e negociam a taxa com o fornecedor**.
- API exposta → **sim**, tratada como superfície (auth/authz/rate-limit).
- Stack → **FastAPI + frontend web leve**, em Docker, múltiplas instâncias, config via env vars.

## 9. Toggles de defesa implementados (Aula 5)

- `input_validation` — filtro de entrada ingênuo (chat) + separação de confiança (documento, RAG: trata o recuperado/anexado como dado, isola RAG por tenant).
- `output_validation` — redige segredo, escapa HTML (XSS) e valida/sandboxa o SQL gerado antes de executar (pipeline de código).
- `least_privilege` — confirmação humana para ação de alto impacto (multi-agent: ignora instrução de outro agente, aplica só o desconto padrão).
- `api_security` — autorização por recurso (contém IDOR) + rate limit por cliente (contém LLM10) na API exposta.

> "Guardrails" (item 4 das 5 camadas do `lab/aula5/README.md`) não virou um toggle isolado — é tratado como a **combinação** das camadas acima; monitoramento é o próprio painel de logs (sempre ativo, não é on/off).
