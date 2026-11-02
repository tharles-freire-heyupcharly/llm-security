"""Superfície 6 — API do Histórico (API de LLM exposta).

VULN: IDOR / autorização por objeto quebrada (alimenta LLM06 — agência sem
autorização) — GET /historico/{matricula} nunca confere se quem está
chamando tem relação com aquela matrícula; qualquer token (ou nenhum) lê o
histórico de qualquer aluno.
VULN: LLM10 (Consumo ilimitado) — não há limite de taxa; o contador de
chamadas devolvido na resposta deixa visível quão barato é varrer todas as
matrículas sequencialmente.
"""
from fastapi import APIRouter

from .. import ollama_client

router = APIRouter()

# Dados sintéticos — nenhuma relação com pessoas reais.
_HISTORICO = {
    "2024001": {"nome": "Ana Beatriz Souza", "curso": "Mestrado em Ciência da Computação",
                "disciplinas": ["Segurança em Sistemas de IA", "Algoritmos Avançados"], "cr": 8.7},
    "2024002": {"nome": "Diego Ramos Ferreira", "curso": "Mestrado em Engenharia de Materiais",
                "disciplinas": ["Processos de Síntese", "Metodologia de Pesquisa"], "cr": 7.9},
    "2024003": {"nome": "Juliana Castro Lima", "curso": "Mestrado em Educação",
                "disciplinas": ["Avaliação Formativa", "Estatística Aplicada"], "cr": 9.1},
}

# VULN: LLM10 — contador global em memória, só para tornar visível o custo de
# uma varredura; não é usado para bloquear nada.
_contador_chamadas = {"total": 0}


@router.get("/surfaces/api-exposed")
def api_exposed_page():
    linhas = "\n".join(
        f'<li><a href="/historico/{m}">/historico/{m}</a></li>' for m in _HISTORICO
    )
    return _pagina_simples(
        titulo="API do Histórico — API de LLM exposta",
        corpo=f"""
        <p>Endpoint <code>GET /historico/&#123;matricula&#125;</code> — nenhuma
        matrícula é mais protegida que outra, e não há limite de chamadas.</p>
        <p>Matrículas de exemplo:</p>
        <ul>{linhas}</ul>
        <p>Dica: troque o número da matrícula na URL (ou tente uma que não está
        na lista) e observe o contador de chamadas subir a cada tentativa.</p>
        """,
    )


@router.get("/historico/{matricula}")
def historico(matricula: str):
    _contador_chamadas["total"] += 1
    registro = _HISTORICO.get(matricula)
    if registro is None:
        resumo = "Matrícula não encontrada neste histórico sintético."
    else:
        # VULN: nenhuma verificação de que o chamador é o próprio aluno, a
        # secretaria ou o orientador — qualquer requisição recebe o resumo.
        resumo = ollama_client.chat(
            messages=[{
                "role": "user",
                "content": (
                    f"Resuma em 2 frases o histórico do aluno {registro['nome']}, "
                    f"curso {registro['curso']}, CR {registro['cr']}, "
                    f"disciplinas: {', '.join(registro['disciplinas'])}."
                ),
            }],
            system="Você resume históricos escolares de forma objetiva, em português.",
        )
    return {
        "matricula": matricula,
        "registro_bruto": registro,
        "resumo_llm": resumo,
        "total_de_chamadas_desde_o_boot": _contador_chamadas["total"],
    }


def _pagina_simples(titulo: str, corpo: str) -> "HTMLResponse":
    from fastapi.responses import HTMLResponse
    return HTMLResponse(f"""<!doctype html>
<html lang="pt-br"><head><meta charset="utf-8">
<title>{titulo} — Campus Aurora</title>
<link rel="stylesheet" href="/static/app.css"></head>
<body>
<header><h1>Campus Aurora — laboratório de segurança em LLMs</h1>
<p>App didático com Ollama local — seis superfícies de ataque para os Trabalhos 1 e 2 do mestrado.</p></header>
<main><a class="back" href="/">&larr; voltar</a>
<div class="card"><h2>{titulo} <span class="badge">IDOR</span><span class="badge">LLM10</span></h2>
{corpo}</div></main></body></html>""")
