#!/usr/bin/env python3
"""Laboratório 3 — Acervo de teses: busca por semelhança não pergunta quem pode ver
(Aula 5; OWASP 2025: LLM08 Fraquezas de vetores e embeddings, LLM01 injeção indireta, LLM02).

No Acervo Aurora (RAG), com SimLLM (simulador didático, NÃO um modelo real):
  1. um documento indexado ("Manual do mestrando") traz instrução oculta que manda recomendar
     um formulário externo (link de phishing fictício);
  2. a busca por semelhança devolve a tese sob EMBARGO DE PATENTE de outro programa.

Com --defesa: o índice é construído a partir de documentos filtrados por programa ANTES da busca,
e documentos com instruções ocultas vão para QUARENTENA na indexação.

Uso:
  python3 aula5/lab3_acervo_rag.py
  python3 aula5/lab3_acervo_rag.py --defesa
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from campus import dados, defesas, narrar  # noqa: E402
from campus.llm import SimLLM  # noqa: E402

ALUNO = "A-1001"  # Marina Tavares, PPG-Computação
PERGUNTA_1 = "Como solicito bolsa e qual o prazo de qualificação segundo o Manual do mestrando?"
PERGUNTA_2 = "Existe estudo sobre biossensor de baixo custo para triagem? Qual o método e há patente?"
SYSTEM = "Você é o assistente do Acervo Aurora. Responda com base nos documentos recuperados."


def _bloco(d):
    return "[DOC {} | {} | {}]\n{}\n[/DOC]".format(d["id"], d["programa"], d["titulo"], d["texto"])


def consultar(pergunta, defesa):
    programa = dados.ALUNOS[ALUNO]["programa"]
    acervo = list(dados.ACERVO)
    quarentenados = []
    if defesa:
        acervo = defesas.filtrar_por_programa(acervo, programa)   # permissão ANTES da busca
        acervo, quarentenados = defesas.quarentena(acervo)         # instruções ocultas
    indice = dados.Indice(acervo)
    achados = indice.buscar(pergunta, k=2)
    contexto = "Documentos recuperados:\n" + ("\n".join(_bloco(d) for d in achados) or "(nenhum)")
    resp = SimLLM().gerar([{"role": "system", "content": SYSTEM},
                           {"role": "user", "content": pergunta + "\n\n" + contexto}])
    return {"recuperados": [d["id"] for d in achados], "resposta": resp,
            "quarentena": [d["id"] for d in quarentenados]}


def executar(defesa=False):
    r1 = consultar(PERGUNTA_1, defesa)
    r2 = consultar(PERGUNTA_2, defesa)
    return {"manual": r1, "embargo": r2,
            "link_externo": "bolsa-aurora.example" in r1["resposta"],
            "vazou_embargo": "PAT-SIM-0042" in r2["resposta"]}


def main(argv=None):
    args = narrar.ler_argumentos(__doc__, argv)
    r = executar(args.defesa)
    narrar.cabecalho("Laboratório 3 — Acervo de teses", args.defesa)

    narrar.secao("ATAQUE")
    narrar.linha("Aluna {} ({}) consulta o Acervo.".format(ALUNO, dados.ALUNOS[ALUNO]["programa"]))
    narrar.linha("1) " + PERGUNTA_1)
    narrar.linha("2) " + PERGUNTA_2)

    narrar.secao("O QUE ACONTECEU")
    for rotulo, k in (("1) Manual envenenado", "manual"), ("2) Tese embargada", "embargo")):
        narrar.linha(rotulo + " — documentos recuperados: " + (", ".join(r[k]["recuperados"]) or "nenhum"))
        narrar.linha(r[k]["resposta"], 4)
    if r["link_externo"]:
        narrar.linha("<-- O assistente recomendou um link externo plantado dentro de um documento indexado.")
    if r["vazou_embargo"]:
        narrar.linha("<-- Trecho de tese sob embargo (PPG-Saúde) foi entregue a aluna de outro programa.")
    if args.defesa:
        narrar.linha("Em quarentena na indexação: " + (", ".join(r["manual"]["quarentena"]) or "nenhum"))

    narrar.secao("O QUE OBSERVAR")
    if args.defesa:
        narrar.linha("- O filtro por programa foi aplicado ANTES da busca: a tese embargada nem entrou no índice desta aluna.")
        narrar.linha("- A quarentena barrou o Manual, mas custou utilidade: o conteúdo legítimo some até alguém revisar e limpar.")
        narrar.linha("- Guardar o vetor também não anonimiza: em produção, isole por programa e controle quem indexa.")
    else:
        narrar.linha("- A busca mede semelhança, não permissão: a tese embargada era a mais parecida com a pergunta.")
        narrar.linha("- Conteúdo recuperado é DADO não confiável, mas entrou no mesmo texto que as instruções.")
        narrar.linha("- Rode com --defesa para ver o filtro por programa antes da busca e a quarentena.")


if __name__ == "__main__":
    main()
