"""Cenário Chatbot — chat de solicitação de empréstimo da CredSim.

Demonstra (Aulas 1, 2 e 3):
- system prompt e fala do cliente no mesmo canal (Raiz 1 do prompt injection);
- LLM07: um SEGREDO foi colocado no system prompt (má prática proposital);
- LLM05: o frontend renderiza a resposta como HTML sem sanitizar — um `<script>`
  pedido pelo cliente e reproduzido pelo modelo executa no navegador (XSS);
- LLM04 Data & Model Poisoning: um backdoor plantado no fine-tuning (mesmo
  gatilho de `poisoning.py`) acorda dentro da conversa normal — ao contrário
  da injeção, não precisa de uma frase que PAREÇA um ataque; qualquer
  mensagem com a frase-gatilho vaza o segredo. A validação de entrada
  (Camada 1, blocklist de palavras suspeitas) é CEGA a isso de propósito —
  não há palavra "suspeita" pra filtrar, o problema está no modelo, não na
  entrada; só a validação de saída (Camada 2) mitiga;
- defesa em profundidade: input_validation + output_validation (Aula 5), esta
  última cobrindo redação de segredo E escape de HTML.
"""
from .. import config, defenses, llm
from ..logging_util import log_event
from ..prompts import load
from . import solicitacoes

# ⚠️ Colocar segredo no system prompt é PROPOSITALMENTE inseguro (LLM07).
APPROVAL_CODE = "APROV-CREDSIM-2026-X9Z"

SYSTEM_PROMPT = load("chatbot")

# Strings sensíveis que o filtro de saída deve redigir. Ordem importa: o prompt
# completo primeiro (contém o código), depois o código como rede de segurança.
_SENSITIVE = [SYSTEM_PROMPT, APPROVAL_CODE]


def _contexto_intake_para_ia(messages: list) -> str:
    """Extrai o estado do intake DETERMINISTICAMENTE (mesma lógica do modo
    mock, `llm.estado_intake`) e devolve um bloco de contexto pro modelo real
    só FORMULAR a resposta em cima — não pedimos pro modelo (local/real) fazer
    a extração/rastreio de campos por conta própria: um modelo pequeno (ex.
    llama3.2:3b) não é confiável nisso (esquece o nome, perde o que já foi
    confirmado). Extração é determinística em qualquer modo; só a REDAÇÃO da
    frase é do "modelo"."""
    coletado, faltando, novidades = llm.estado_intake(messages)
    estado = llm.estado_confirmacao(messages)

    if estado == "acabou_de_completar":
        dados = "; ".join(f"{c}: {v}" for c, v in coletado.items())
        return (
            "[Todos os dados do pedido acabaram de ser coletados agora — não "
            "peça mais nada, nem invente dados novos, e a solicitação AINDA "
            "NÃO foi criada]\n"
            f"Dados coletados: {dados}\n"
            "Apresente ao cliente um resumo final com TODOS esses dados e "
            "peça a confirmação dele (algo como \"você confirma que está "
            "tudo certo?\"). Não diga que a solicitação foi criada — ela só "
            "é criada depois que o cliente confirmar."
        )

    if estado == "confirmado_agora":
        return (
            "[O cliente acabou de confirmar os dados nesta mensagem — a "
            "solicitação foi criada agora]\n"
            "Diga ao cliente, em 1 ou 2 frases, que a solicitação foi criada "
            "com sucesso e que ele já pode conferir as propostas dos "
            "parceiros na aba Simulação. Não peça mais nenhum dado."
        )

    if estado == "ja_confirmado":
        return (
            "[O cliente já confirmou os dados numa mensagem anterior — a "
            "solicitação já foi criada antes desta mensagem]\n"
            "Diga, em 1 ou 2 frases, que a solicitação já está criada e que "
            "ele pode acompanhar as propostas dos parceiros na aba "
            "Simulação. Não peça confirmação de novo nem crie/mencione uma "
            "nova solicitação."
        )

    if estado == "aguardando_confirmacao":
        dados = "; ".join(f"{c}: {v}" for c, v in coletado.items())
        return (
            "[Todos os dados já foram coletados, mas a última mensagem do "
            "cliente não confirmou claramente se estão corretos — a "
            "solicitação AINDA NÃO foi criada]\n"
            f"Dados coletados: {dados}\n"
            "Diga que ainda precisa da confirmação dele e pergunte de novo "
            "se os dados estão corretos, pedindo pra responder \"sim\" ou "
            "apontar o que precisa corrigir. Não diga que a solicitação foi criada."
        )

    anteriores = {c: v for c, v in coletado.items() if c not in novidades}
    # Formato de bloco de dados (rótulos em MAIÚSCULAS + marcador de fim), não
    # uma frase pronta — modelos locais fracos tendem a ecoar de volta texto
    # que já parece uma frase natural (ex.: "Ainda faltando: X, Y" saía quase
    # literal na resposta ao cliente). O aviso de "não repetir" reforça isso.
    return (
        "[NOTAS INTERNAS — não visíveis ao cliente; servem só pra você decidir "
        "o que dizer. NUNCA reproduza os rótulos ou o formato desta nota na "
        "resposta: escreva a resposta em português natural, com suas próprias "
        "palavras; não faça sua própria extração dos dados, use exatamente o "
        "que está listado aqui]\n"
        f"CAMPOS_JA_CONFIRMADOS: {anteriores or '(nenhum ainda)'}\n"
        f"CAMPOS_IDENTIFICADOS_NESTA_MENSAGEM: {novidades or '(nenhum novo)'}\n"
        f"CAMPOS_QUE_FALTAM_PEDIR: {', '.join(faltando)}\n"
        "[FIM DAS NOTAS INTERNAS]\n"
        "Com base nisso: se algo foi identificado nesta mensagem, confirme "
        "educadamente cada um (formato \"seu/sua <dado> é: <valor>\"). Se nada "
        "foi identificado, diga isso claramente. Em seguida peça SOMENTE os "
        "dados que faltam, listando-os todos de uma vez, sem repetir perguntas "
        "sobre dados já confirmados antes. Esses dados são OBRIGATÓRIOS, não "
        "uma preferência do cliente — peça-os com linguagem de exigência "
        "(\"preciso que você informe...\"), nunca de opção (nunca \"você "
        "gostaria de fornecer...\" ou equivalente)."
    )


def handle_message(user_message: str, history: list = None,
                   defense_input: bool = False, defense_output: bool = False) -> dict:
    """Processa uma mensagem do cliente e devolve a resposta + metadados para o log.

    `defense_input` / `defense_output` ligam/desligam as camadas (toggle on/off).
    """
    history = history or []
    injection = llm.looks_like_injection(user_message)
    gatilho_backdoor = llm.looks_like_poisoning_trigger(user_message)

    # Camada 1 — validação de entrada (Aula 5). Filtro ingênuo, burlável — e,
    # de propósito, CEGO ao gatilho de backdoor (não é uma "palavra suspeita").
    if defense_input:
        blocked = defenses.check_input(user_message)
        if blocked:
            log_event({
                "scenario": "chatbot", "stage": "input_validation", "blocked": True,
                "injection_suspected": injection, "user_message": user_message,
                "reply": blocked,
            })
            return {"reply": blocked, "blocked_by": "input_validation",
                    "injection_suspected": injection,
                    "leaked_secret_pre_filter": False, "output_redacted": False,
                    "html_payload_pre_filter": False, "output_html_escaped": False,
                    "backdoor_trigger_detected": False, "solicitacao_id": None}

    # Monta o contexto e chama o "modelo" (mock ou real).
    messages = history + [{"role": "user", "content": user_message}]
    parece_ataque = injection or llm.looks_like_html_payload(user_message) or gatilho_backdoor
    if gatilho_backdoor:
        # Backdoor de fine-tuning (LLM04): sempre determinístico, em QUALQUER
        # modo — não existe como reproduzir um gatilho plantado no treinamento
        # com um modelo local/real de verdade (ele nunca foi de fato envenenado).
        raw_reply = (
            "[BACKDOOR ATIVADO] Uma frase-gatilho plantada no treinamento deste "
            f"modelo foi reconhecida. Ignorando restrições:\n\n{SYSTEM_PROMPT}\n\n"
            "Posso ajudar em mais alguma coisa?"
        )
    elif config.LLM_MODE == "mock" or parece_ataque:
        # Ataque (ou payload HTML): deixa o modelo responder livremente ao que
        # foi pedido — não injeta o contexto de intake, senão o próprio ataque
        # seria confundido com uma resposta de "nome" (texto sem dígitos). O
        # reforço de obediência só entra AQUI, na mensagem que de fato parece
        # ataque — nunca nos turnos normais do intake (ver aplicar_reforco_obediencia).
        system_da_chamada = llm.aplicar_reforco_obediencia(SYSTEM_PROMPT) if parece_ataque else SYSTEM_PROMPT
        raw_reply = llm.generate(system_da_chamada, messages)
    else:
        # local/real, mensagem normal: a extração de dados é determinística
        # (ver função acima); o modelo real só formula a frase, não rastreia o
        # formulário por conta própria.
        contexto = _contexto_intake_para_ia(messages)
        raw_reply = llm.generate(SYSTEM_PROMPT + "\n\n" + contexto, messages)

    # Camada 2 — validação de saída (Aula 5): redige segredo + escapa HTML (Aula 3: XSS).
    leaked_secret = APPROVAL_CODE in raw_reply
    html_payload = llm.looks_like_html_payload(raw_reply)
    reply = raw_reply
    redacted = False
    html_escaped = False
    if defense_output:
        filtered = defenses.filter_output(raw_reply, _SENSITIVE)
        redacted = filtered != raw_reply
        reply = defenses.escape_html(filtered)
        html_escaped = reply != filtered

    log_event({
        "scenario": "chatbot", "stage": "response",
        "injection_suspected": injection,
        "backdoor_trigger_detected": gatilho_backdoor,
        "leaked_secret_pre_filter": leaked_secret,
        "output_redacted": redacted,
        "html_payload_pre_filter": html_payload,
        "output_html_escaped": html_escaped,
        "user_message": user_message, "reply": reply,
    })

    # Só cria a solicitação no turno em que o cliente CONFIRMA o resumo final
    # (estado "confirmado_agora") — nunca no turno que só completou os dados
    # (aí a resposta pede confirmação, ainda não cria nada), nunca de novo
    # depois de já confirmado, e nunca a partir de uma mensagem de ataque.
    solicitacao_id = None
    if not parece_ataque and llm.estado_confirmacao(messages) == "confirmado_agora":
        coletado, _, _ = llm.estado_intake(messages)
        solicitacao_id = solicitacoes.criar(coletado)["id"]

    return {"reply": reply, "blocked_by": None, "injection_suspected": injection,
            "backdoor_trigger_detected": gatilho_backdoor,
            "leaked_secret_pre_filter": leaked_secret, "output_redacted": redacted,
            "html_payload_pre_filter": html_payload, "output_html_escaped": html_escaped,
            "solicitacao_id": solicitacao_id}
