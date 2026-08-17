"""Backend FastAPI da CredSim.

Serve a interface web e expõe as 6 superfícies (chat, RAG, agente de análise,
multi-agent, pipeline de código e a própria API) + toggles de defesa + logs, além dos
fundamentos da Aula 1 (tokenização, geração probabilística, alucinação). Este backend é,
ele mesmo, a superfície "API exposta" (Aula 3).
"""
from pathlib import Path
from typing import List

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from labcore import config, logging_util, pdf_utils, store
from labcore.scenarios import (
    ajuda, alucinacao, ambiguidade, analise, api_exposta, atencao, canal_unico, chatbot,
    credit, documento, filtro, geracao, negociacao, pipeline_credito, poisoning, rag,
    seed_demo, solicitacoes, suporte, supply_chain, tokenizer,
)

app = FastAPI(title="CredSim Lab — CredSim (6 superfícies)")

# Popula solicitações de exemplo para a página Interno > Simulações não
# começar vazia. Chamada aqui, no nível de módulo (não num endpoint, nem num
# evento `startup` do FastAPI) para rodar UMA VEZ por processo — `import` é
# cacheado, então isso vale inclusive quando a suíte de testes sobe vários
# `TestClient(app)` (todos reusam este módulo já importado). Um `startup`
# rodaria de novo a cada teste que usa a fixture `client` (que dispara esses
# eventos), reenchendo o store depois do `store.reset()` da fixture.
seed_demo.popular_exemplos()

# Estado dos toggles de defesa (em memória; controlável pela UI e pelos notebooks).
_defenses = {
    "input_validation": config.DEFENSE_INPUT_VALIDATION,
    "output_validation": config.DEFENSE_OUTPUT_VALIDATION,
    "least_privilege": config.DEFENSE_LEAST_PRIVILEGE,
    "api_security": config.DEFENSE_API_SECURITY,
    "guardrails": config.DEFENSE_GUARDRAILS,
}

_FRONTEND = Path(__file__).resolve().parent.parent / "frontend" / "index.html"

# Arquivos observados pelo live-reload de desenvolvimento (ver /api/dev/mtime).
_APP_DIR = Path(__file__).resolve().parent.parent
_WATCH_FILES = [_FRONTEND, Path(__file__).resolve()]
_WATCH_DIRS = [_APP_DIR / "labcore"]


class ChatRequest(BaseModel):
    message: str
    history: List[dict] = []
    usuario: str = ""


class DefenseState(BaseModel):
    input_validation: bool
    output_validation: bool
    least_privilege: bool = False
    api_security: bool = False
    guardrails: bool = False


_LLM_MODES = ("mock", "local", "real")


class LlmModeRequest(BaseModel):
    mode: str


# As únicas duas financeiras com documento cadastrado em labcore/scenarios/rag.py.
_TENANTS = ("financeira-A", "financeira-B")


class TenantRequest(BaseModel):
    tenant: str


class SimulateRequest(BaseModel):
    renda: float = 0
    valor: float = 0
    prazo: int = 12




class RagRequest(BaseModel):
    query: str = ""


class AnaliseRequest(BaseModel):
    solicitacao_id: int = 1
    observacao: str = ""


class NegociarRequest(BaseModel):
    tema: str = "mercado"
    solicitacao_id: int = None
    nome: str = "Cliente Teste"
    cpf: str = "000.000.000-00"
    renda: float = 6000


class PublicaRequest(BaseModel):
    cliente_id: str
    pergunta: str


class TokenizarRequest(BaseModel):
    texto: str = ""
    model: str = "claude-opus-4-8"


class GerarRequest(BaseModel):
    inicio: str = "o"
    seed: int = 0


class PerguntaRequest(BaseModel):
    pergunta: str = ""


class AmbiguidadeRequest(BaseModel):
    exemplo: str = "laranja"


class AmbiguidadeTextoRequest(BaseModel):
    texto: str = ""


class FiltroRequest(BaseModel):
    texto: str = ""


class FiltroBurlarRequest(BaseModel):
    palavra: str = ""


class FiltroGrafiaRequest(BaseModel):
    texto: str = ""


class CanalUnicoRequest(BaseModel):
    mensagem: str = ""


class SupplyChainRequest(BaseModel):
    origem: str = "adulterado"


class PoisoningRequest(BaseModel):
    prompt: str = ""


class SuporteRequest(BaseModel):
    pergunta: str = ""
    historico: List[dict] = []
    solicitante: str = ""


class AjudaRequest(BaseModel):
    pergunta: str = ""


class FinalizarSolicitacaoRequest(BaseModel):
    nome: str = ""
    cpf: str = ""
    email: str = ""
    renda: float = 0
    valor: float = 0
    prazo: int = 12
    documento_conteudo: str = ""


class AceitarPropostaRequest(BaseModel):
    proposta_id: str


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return _FRONTEND.read_text(encoding="utf-8")


@app.get("/api/info")
def info():
    modelo_por_modo = {"real": config.LLM_MODEL, "local": config.OLLAMA_MODEL, "mock": "mock"}
    return {
        "tenant": config.TENANT_ID,
        "llm_mode": config.LLM_MODE,
        "model": modelo_por_modo.get(config.LLM_MODE, "mock"),
    }


@app.get("/api/defenses")
def get_defenses():
    return _defenses


@app.post("/api/defenses")
def set_defenses(state: DefenseState):
    _defenses["input_validation"] = state.input_validation
    _defenses["output_validation"] = state.output_validation
    _defenses["least_privilege"] = state.least_privilege
    _defenses["api_security"] = state.api_security
    _defenses["guardrails"] = state.guardrails
    return _defenses


@app.get("/api/llm-mode")
def get_llm_mode():
    return {"mode": config.LLM_MODE, "modes": _LLM_MODES}


@app.post("/api/llm-mode")
def set_llm_mode(req: LlmModeRequest):
    """Troca o motor de IA em runtime (mock/local/real) — sem reiniciar o
    processo, para o professor alternar ao vivo entre demo mock e IA real."""
    if req.mode not in _LLM_MODES:
        raise HTTPException(status_code=400, detail=f"modo inválido: {req.mode!r}")
    config.LLM_MODE = req.mode
    return {"mode": config.LLM_MODE, "modes": _LLM_MODES}


@app.get("/api/tenant")
def get_tenant():
    return {"tenant": config.TENANT_ID, "tenants": _TENANTS}


@app.post("/api/tenant")
def set_tenant(req: TenantRequest):
    """Troca a financeira ativa em runtime — a demo de vazamento entre tenants
    do RAG (Aula 4) não precisa de um container por financeira; uma instância
    alterna entre elas e consulta a MESMA base mock (labcore/scenarios/rag.py)."""
    if req.tenant not in _TENANTS:
        raise HTTPException(status_code=400, detail=f"tenant inválido: {req.tenant!r}")
    config.TENANT_ID = req.tenant
    return {"tenant": config.TENANT_ID, "tenants": _TENANTS}


@app.post("/api/chat")
def chat(req: ChatRequest):
    return chatbot.handle_message(
        req.message,
        history=req.history,
        defense_input=_defenses["input_validation"],
        defense_output=_defenses["output_validation"],
        defense_guardrails=_defenses["guardrails"],
        usuario=req.usuario or None,
    )


@app.get("/api/chat/system-prompt")
def chat_system_prompt():
    """Devolve o system prompt real do chat (Tour OWASP LLM01/LLM07) — ele carrega
    um segredo colado de propósito (`APPROVAL_CODE`), para demonstrar system
    prompt leakage. Não é usado pelo backend para nada além de exibição na UI."""
    return {"system_prompt": chatbot.SYSTEM_PROMPT}


@app.post("/api/simulate")
def simulate(req: SimulateRequest):
    result = credit.simulate(req.renda, req.valor, req.prazo)
    logging_util.log_event({
        "scenario": "credito", "stage": "simulacao",
        "renda": req.renda, "valor": req.valor, "prazo": req.prazo,
        "aprovado": result["aprovado"],
    })
    return result


@app.post("/api/validate-doc")
async def validate_doc(arquivo: UploadFile = File(...)):
    conteudo_pdf = await arquivo.read()
    try:
        texto = pdf_utils.extrair_texto(conteudo_pdf)
    except pdf_utils.PdfInvalidoError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return documento.validate_document(texto, defense_input=_defenses["input_validation"])


@app.post("/api/suporte")
def suporte_endpoint(req: SuporteRequest):
    return suporte.perguntar(
        req.pergunta, historico=req.historico,
        solicitante=req.solicitante, defense_api_security=_defenses["api_security"],
    )


@app.post("/api/ajuda")
def ajuda_endpoint(req: AjudaRequest):
    return ajuda.perguntar(req.pergunta)


@app.post("/api/solicitacao/finalizar")
def finalizar_solicitacao(req: FinalizarSolicitacaoRequest):
    """Fluxo multi-agent: validação de documento -> simulação de crédito ->
    agente de aprovação (que notifica por e-mail via MCP mockado se aprovar)."""
    cliente = {
        "nome": req.nome, "cpf": req.cpf, "email": req.email,
        "renda": req.renda, "valor": req.valor, "prazo": req.prazo,
    }
    return pipeline_credito.processar_solicitacao(
        cliente, req.documento_conteudo,
        defense_input=_defenses["input_validation"],
        defense_output=_defenses["output_validation"],
    )


@app.get("/api/solicitacoes")
def listar_solicitacoes():
    return store.listar()


@app.get("/api/solicitacoes/{solicitacao_id}")
def obter_solicitacao(solicitacao_id: int, solicitante: str = None):
    """`solicitante` é opcional: a visão Interno (staff) chama sem ele — vê
    qualquer solicitação, sempre, por design. Só a página Simulação (cliente
    final) manda a própria identidade — é ali que o IDOR faz sentido: sem
    `defense_api_security`, qualquer ID retorna os dados de qualquer cliente
    (API mapping: o endpoint nunca é anunciado como tela de segurança, mas
    está lá, respondendo, pra quem souber "mapear" e trocar o ID na URL)."""
    solicitacao = store.obter(solicitacao_id)
    if solicitacao is None:
        raise HTTPException(status_code=404, detail="solicitação não encontrada")
    if _defenses["api_security"] and solicitante:
        dono = (solicitacao.get("usuario") or "").strip().lower()
        if dono and dono != solicitante.strip().lower():
            raise HTTPException(status_code=403, detail="Acesso negado: você não é o dono desta solicitação.")
    return solicitacao


@app.post("/api/solicitacoes/{solicitacao_id}/aceitar")
def aceitar_proposta_endpoint(solicitacao_id: int, req: AceitarPropostaRequest):
    try:
        return solicitacoes.aceitar_proposta(solicitacao_id, req.proposta_id)
    except ValueError as exc:
        status = 404 if "não encontrada" in str(exc) else 400
        raise HTTPException(status_code=status, detail=str(exc))


@app.post("/api/solicitacoes/{solicitacao_id}/finalizar")
async def finalizar_solicitacao_por_id(
    solicitacao_id: int, cpf: str = Form(""), email: str = Form(""), arquivo: UploadFile = File(...),
):
    conteudo_pdf = await arquivo.read()
    try:
        texto = pdf_utils.extrair_texto(conteudo_pdf)
    except pdf_utils.PdfInvalidoError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    try:
        return solicitacoes.finalizar(
            solicitacao_id, cpf, email, texto,
            defense_input=_defenses["input_validation"], defense_output=_defenses["output_validation"],
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.post("/api/rag")
def rag_ask(req: RagRequest):
    return rag.ask(req.query, tenant=config.TENANT_ID, defense_input=_defenses["input_validation"])


@app.post("/api/analise")
def analise_endpoint(req: AnaliseRequest):
    resultado = analise.analisar(
        req.solicitacao_id, req.observacao, defense_output=_defenses["output_validation"],
    )
    if "erro" in resultado:
        raise HTTPException(status_code=404, detail=resultado["erro"])
    return resultado


@app.post("/api/negociacao")
def negociacao_endpoint(req: NegociarRequest):
    if req.solicitacao_id is not None:
        solicitacao = store.obter(req.solicitacao_id)
        if solicitacao is None:
            raise HTTPException(status_code=404, detail="solicitação não encontrada")
        c = solicitacao["cliente"]
        cliente = {"nome": c.get("nome"), "cpf": c.get("cpf", "não informado"), "renda": c.get("renda")}
    else:
        cliente = {"nome": req.nome, "cpf": req.cpf, "renda": req.renda}
    return negociacao.negociar(
        req.tema, defense_least_privilege=_defenses["least_privilege"], cliente=cliente,
    )


@app.get("/api/conversas/{conversa_id}")
def conversa(conversa_id: int, solicitante: str = "cliente-A"):
    return api_exposta.get_conversa(
        conversa_id, solicitante, defense_api_security=_defenses["api_security"]
    )


@app.post("/api/publica")
def publica(req: PublicaRequest):
    return api_exposta.chamar_api_publica(
        req.cliente_id, req.pergunta, defense_api_security=_defenses["api_security"]
    )


@app.post("/api/tokenizar")
def tokenizar(req: TokenizarRequest):
    return tokenizer.contar(req.texto, req.model)


@app.post("/api/gerar")
def gerar(req: GerarRequest):
    return geracao.gerar(req.inicio, seed=req.seed)


@app.get("/api/atencao")
def atencao_endpoint():
    return atencao.pesos_atencao()


@app.post("/api/alucinacao")
def alucinar(req: PerguntaRequest):
    return alucinacao.perguntar(req.pergunta)


@app.post("/api/filtro")
def filtro_endpoint(req: FiltroRequest):
    return filtro.testar(req.texto)


@app.post("/api/filtro/burlar")
def filtro_burlar_endpoint(req: FiltroBurlarRequest):
    return filtro.sugerir_burla(req.palavra)


@app.post("/api/filtro/grafia")
def filtro_grafia_endpoint(req: FiltroGrafiaRequest):
    return filtro.testar_disfarce(req.texto)


@app.post("/api/ambiguidade")
def ambiguidade_endpoint(req: AmbiguidadeRequest):
    return ambiguidade.perguntar(req.exemplo)


@app.post("/api/ambiguidade/texto")
def ambiguidade_texto_endpoint(req: AmbiguidadeTextoRequest):
    return ambiguidade.perguntar_texto(req.texto)


@app.post("/api/canal-unico")
def canal_unico_endpoint(req: CanalUnicoRequest):
    return canal_unico.perguntar(req.mensagem)


@app.post("/api/supply-chain")
def supply_chain_endpoint(req: SupplyChainRequest):
    return supply_chain.verificar(req.origem)


@app.post("/api/poisoning")
def poisoning_endpoint(req: PoisoningRequest):
    return poisoning.perguntar(req.prompt)


@app.get("/api/dev/mtime")
def dev_mtime():
    """Última modificação entre frontend/backend/labcore — usado pelo live-reload do
    navegador durante o desenvolvimento (o front faz polling e recarrega ao mudar)."""
    arquivos = list(_WATCH_FILES) + [p for d in _WATCH_DIRS for p in d.rglob("*.py")]
    return {"mtime": max((p.stat().st_mtime for p in arquivos if p.exists()), default=0)}


@app.get("/api/logs")
def logs():
    return logging_util.get_events()


@app.post("/api/reset")
def reset():
    logging_util.clear()
    api_exposta.reset()
    store.reset()
    return {"ok": True}
