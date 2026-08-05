"""Backend FastAPI da CredSim.

Serve a interface web e expõe as 6 superfícies (chat, RAG, agente de análise,
multi-agent, pipeline de código e a própria API) + toggles de defesa + logs, além dos
fundamentos da Aula 1 (tokenização, geração probabilística, alucinação). Este backend é,
ele mesmo, a superfície "API exposta" (Aula 3).
"""
from pathlib import Path
from typing import List

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from labcore import config, logging_util
from labcore.scenarios import (
    alucinacao, ambiguidade, analise, api_exposta, atencao, canal_unico, chatbot, credit,
    documento, filtro, geracao, negociacao, poisoning, rag, supply_chain, tokenizer,
)

app = FastAPI(title="CredSim Lab — CredSim (6 superfícies)")

# Estado dos toggles de defesa (em memória; controlável pela UI e pelos notebooks).
_defenses = {
    "input_validation": config.DEFENSE_INPUT_VALIDATION,
    "output_validation": config.DEFENSE_OUTPUT_VALIDATION,
    "least_privilege": config.DEFENSE_LEAST_PRIVILEGE,
    "api_security": config.DEFENSE_API_SECURITY,
}

_FRONTEND = Path(__file__).resolve().parent.parent / "frontend" / "index.html"

# Arquivos observados pelo live-reload de desenvolvimento (ver /api/dev/mtime).
_APP_DIR = Path(__file__).resolve().parent.parent
_WATCH_FILES = [_FRONTEND, Path(__file__).resolve()]
_WATCH_DIRS = [_APP_DIR / "labcore"]


class ChatRequest(BaseModel):
    message: str
    history: List[dict] = []


class DefenseState(BaseModel):
    input_validation: bool
    output_validation: bool
    least_privilege: bool = False
    api_security: bool = False


class SimulateRequest(BaseModel):
    renda: float = 0
    valor: float = 0
    prazo: int = 12


class DocRequest(BaseModel):
    content: str = ""


class RagRequest(BaseModel):
    query: str = ""


class AnaliseRequest(BaseModel):
    id: int = 1
    nome: str = "Cliente Teste"
    observacao: str = ""


class NegociarRequest(BaseModel):
    tema: str = "mercado"


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


class CanalUnicoRequest(BaseModel):
    mensagem: str = ""


class SupplyChainRequest(BaseModel):
    origem: str = "adulterado"


class PoisoningRequest(BaseModel):
    prompt: str = ""


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return _FRONTEND.read_text(encoding="utf-8")


@app.get("/api/info")
def info():
    return {
        "tenant": config.TENANT_ID,
        "llm_mode": config.LLM_MODE,
        "model": config.LLM_MODEL if config.LLM_MODE == "real" else "mock",
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
    return _defenses


@app.post("/api/chat")
def chat(req: ChatRequest):
    return chatbot.handle_message(
        req.message,
        history=req.history,
        defense_input=_defenses["input_validation"],
        defense_output=_defenses["output_validation"],
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
def validate_doc(req: DocRequest):
    return documento.validate_document(req.content, defense_input=_defenses["input_validation"])


@app.post("/api/rag")
def rag_ask(req: RagRequest):
    return rag.ask(req.query, tenant=config.TENANT_ID, defense_input=_defenses["input_validation"])


@app.post("/api/analise")
def analise_endpoint(req: AnaliseRequest):
    cliente = {"id": req.id, "nome": req.nome, "observacao": req.observacao}
    return analise.analisar(cliente, defense_output=_defenses["output_validation"])


@app.post("/api/negociacao")
def negociacao_endpoint(req: NegociarRequest):
    return negociacao.negociar(req.tema, defense_least_privilege=_defenses["least_privilege"])


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
    return {"ok": True}
