"""Agente de Ajuda — dúvidas sobre COMO USAR o CredSim.

Diferente dos outros cenários (que demonstram uma vulnerabilidade de
segurança), este agente tem propósito de PRODUTO: responde perguntas de
navegação — onde simular um empréstimo, como enviar um documento, o que são
as propostas dos parceiros, o que é a liberação do dinheiro etc. Ele não
responde sobre condições de crédito específicas nem sobre dados de um
cliente/pedido — isso é papel do assistente de solicitação (página Chat) ou
do suporte (página Suporte).

RAG de verdade, no mesmo espírito mock já usado em `rag.py`/`suporte.py`
(retrieval por interseção de palavras, sem embeddings de verdade):
- `_BASE` é a base de conhecimento — um documento curto por página/fluxo/
  conceito do app, descrevendo o produto como ele funciona HOJE;
- `buscar()` pontua cada documento pelas palavras da pergunta que aparecem
  nele (normalizando acento e ignorando palavras de função em português) e
  devolve os mais relevantes — sem nada relevante, devolve lista vazia;
- mock: a resposta é montada direto do(s) documento(s) recuperado(s);
- local/real: os mesmos documentos viram um bloco de "notas internas" (mesmo
  padrão de `chatbot.py:_contexto_intake_para_ia`) e o LLM só FORMULA a
  resposta em cima deles — instruído a dizer que não sabe, em vez de
  inventar, quando nada relevante foi recuperado.
"""
import string
import unicodedata

from .. import config, llm
from ..logging_util import log_event
from ..prompts import load

# Base de conhecimento: um "documento" por página/fluxo/conceito do app hoje.
# `termos` é um pequeno glossário de sinônimos/variações que reforça a busca
# (formas que o cliente pode digitar mas que não aparecem no texto corrido) —
# ainda é um mock determinístico por palavra, não um índice de embeddings.
_BASE = [
    {
        "topico": "inicio",
        "titulo": "Página Início",
        "conteudo": (
            "A página Início apresenta a CredSim e traz o botão \"Solicitar "
            "empréstimo\", que leva direto para a página Chat. A navegação "
            "entre todas as áreas — Chat, Simulação, Documento, Suporte e "
            "Ajuda — fica sempre disponível no menu lateral."
        ),
        "termos": ["home", "página inicial", "menu lateral", "navegação"],
    },
    {
        "topico": "chat_intake",
        "titulo": "Chat — assistente de solicitação",
        "conteudo": (
            "Na página Chat você conversa com o assistente de solicitação de "
            "empréstimo, que pergunta um dado por vez, nesta ordem: nome "
            "completo, renda mensal, valor desejado, prazo em meses, agência "
            "bancária e número da conta. Quando todos os dados são "
            "coletados, o assistente cria automaticamente uma solicitação e "
            "mostra um botão \"Ver propostas\" para você ir até a página "
            "Simulação."
        ),
        "termos": ["pedir empréstimo", "solicitar crédito", "dados coletados", "intake", "conversar com o assistente"],
    },
    {
        "topico": "conceito_solicitacao",
        "titulo": "O que é uma solicitação",
        "conteudo": (
            "Uma \"solicitação\" é o pedido de crédito criado ao final do "
            "chat, com os dados do cliente e uma simulação interna. Cada "
            "solicitação tem um número (id) e avança por status diferentes "
            "— propostas disponíveis, aceita, aprovada ou reprovada — "
            "visíveis na página Simulação."
        ),
        "termos": ["pedido", "número do pedido", "id da solicitação"],
    },
    {
        "topico": "como_simular",
        "titulo": "Como simular um empréstimo",
        "conteudo": (
            "Hoje não existe mais um formulário avulso de simulação: para "
            "simular um empréstimo, converse com o assistente na página "
            "Chat informando renda, valor e prazo. A simulação — taxa, "
            "risco, valor sugerido e parcela estimada — é calculada "
            "automaticamente a partir desses dados e aparece no detalhe da "
            "solicitação, na página Simulação."
        ),
        "termos": ["simular", "simulação rápida", "simule", "quero simular", "fazer uma simulação"],
    },
    {
        "topico": "simulacao_lista",
        "titulo": "Simulação — lista de solicitações",
        "conteudo": (
            "A página Simulação lista \"Minhas solicitações\": número, nome "
            "do cliente, status (em uma etiqueta colorida) e o valor/prazo "
            "pedidos. Clique em qualquer item da lista para abrir o "
            "detalhe da solicitação. Se a lista estiver vazia, é porque "
            "ainda falta completar o chat para criar uma solicitação."
        ),
        "termos": ["minhas solicitações", "lista de pedidos", "ver solicitações"],
    },
    {
        "topico": "simulacao_detalhe",
        "titulo": "Detalhe da solicitação",
        "conteudo": (
            "No detalhe de uma solicitação você vê a simulação interna da "
            "CredSim: se o pedido foi pré-aprovado ou precisa de ajuste, o "
            "nível de risco, a taxa mensal, o valor sugerido e a parcela "
            "estimada. Essa simulação é só a referência interna usada para "
            "gerar as ofertas dos parceiros, logo abaixo na mesma tela."
        ),
        "termos": ["risco", "taxa mensal", "pré-aprovado", "ajuste sugerido"],
    },
    {
        "topico": "propostas_parceiros",
        "titulo": "Propostas dos parceiros",
        "conteudo": (
            "Cada solicitação recebe até 4 propostas de financeiras "
            "parceiras fictícias, cada uma com um diferencial: TaxaBaixa "
            "Financeira (menor taxa), CredMax (maior valor liberado), Prazo "
            "Longo Financeira (maior prazo) e FinCerta (condições padrão de "
            "mercado). Cada proposta mostra taxa mensal, valor ofertado, "
            "parcela estimada, prazo e um parecer em texto — os números "
            "variam porque cada parceiro aplica um ajuste próprio em cima "
            "da simulação interna."
        ),
        "termos": ["parceiros", "ofertas", "financeiras parceiras", "comparar propostas", "diferença entre propostas"],
    },
    {
        "topico": "aceitar_proposta",
        "titulo": "Como aceitar uma proposta",
        "conteudo": (
            "No detalhe da solicitação, cada proposta tem um botão "
            "\"Aceitar esta proposta\" — clique no parceiro escolhido para "
            "confirmar. Só é possível aceitar uma proposta por solicitação; "
            "depois de aceitar, as demais ficam esmaecidas na tela e surge "
            "um botão \"Ir para Documento\" para seguir com o pedido."
        ),
        "termos": ["aceitar oferta", "escolher parceiro", "confirmar proposta", "aceito"],
    },
    {
        "topico": "depois_de_aceitar",
        "titulo": "O que acontece depois de aceitar uma proposta",
        "conteudo": (
            "Depois de aceitar uma proposta, a solicitação muda para o "
            "status \"aceita\" e aparece um botão \"Ir para Documento\" — o "
            "próximo passo é enviar o documento de identidade na página "
            "Documento e, em seguida, finalizar a solicitação para que ela "
            "seja aprovada ou reprovada."
        ),
        "termos": ["próximo passo", "o que fazer depois", "após aceitar a proposta"],
    },
    {
        "topico": "documento_upload",
        "titulo": "Documento — envio e validação",
        "conteudo": (
            "Na página Documento você envia um arquivo PDF de identidade e "
            "clica em \"Validar documento\"; o texto do PDF é extraído no "
            "servidor e analisado antes do resultado aparecer (status e "
            "mensagem). Use os PDFs de exemplo em lab/app_v2/exemplos/ para "
            "testar o fluxo."
        ),
        "termos": ["upload", "enviar documento", "pdf", "validar documento", "documento de identidade"],
    },
    {
        "topico": "documentos_aceitos",
        "titulo": "Quais documentos enviar",
        "conteudo": (
            "Para finalizar um pedido, envie um documento de identidade em "
            "PDF — nesta demonstração, qualquer um dos PDFs de exemplo em "
            "lab/app_v2/exemplos/ serve. Não é preciso enviar CPF ou "
            "comprovante de renda como arquivo separado: esses dados já "
            "vêm do chat e do formulário de finalização."
        ),
        "termos": ["que documento enviar", "identidade", "comprovante de renda", "cpf", "formato aceito"],
    },
    {
        "topico": "liberacao_dinheiro",
        "titulo": "Liberação do dinheiro",
        "conteudo": (
            "A liberação do dinheiro é o último passo do fluxo, disparado "
            "automaticamente ao finalizar uma solicitação aprovada. Ela "
            "simula uma transferência do valor liberado para a agência e "
            "conta informadas no chat; sem agência/conta cadastradas, a "
            "transferência fica pendente, e pedidos reprovados não geram "
            "nenhuma transferência."
        ),
        "termos": ["transferência", "receber o dinheiro", "pagamento", "agência e conta", "transferir valor"],
    },
    {
        "topico": "finalizar_solicitacao",
        "titulo": "Finalizar solicitação",
        "conteudo": (
            "O card \"Finalizar solicitação\", na página Documento, fecha o "
            "pedido: escolha a solicitação no menu, confirme CPF e e-mail, "
            "e reaproveite o PDF selecionado acima. Ao clicar em "
            "\"Finalizar solicitação\", o sistema encadeia três agentes — "
            "validação do documento, aprovação e, se aprovado, liberação "
            "do dinheiro — e a solicitação muda de status para aprovada ou "
            "reprovada."
        ),
        "termos": ["finalizar pedido", "finalização", "concluir solicitação", "encadeia agentes", "aprovação do documento", "como funciona a finalização"],
    },
    {
        "topico": "status_solicitacao",
        "titulo": "Status possíveis de uma solicitação",
        "conteudo": (
            "Uma solicitação passa por até quatro status: \"propostas "
            "disponíveis\" (logo após o chat), \"aceita\" (proposta "
            "escolhida, falta o documento), e por fim \"aprovada\" ou "
            "\"reprovada\" (depois de finalizar na página Documento). O "
            "status atual aparece numa etiqueta colorida ao lado do nome "
            "da solicitação."
        ),
        "termos": ["etiqueta de status", "badge", "andamento do pedido"],
    },
    {
        "topico": "suporte",
        "titulo": "Página Suporte",
        "conteudo": (
            "A página Suporte é um chat separado para consultar pedidos já "
            "existentes: pergunte pelo número do pedido, pelo CPF ou pelo "
            "nome do cliente, e o assistente responde com status, valor, "
            "taxa (se aprovado) ou motivo (se reprovado). Diferente do "
            "Chat, o Suporte só consulta — não cria nem altera nada."
        ),
        "termos": ["consultar pedido", "acompanhar pedido", "status do pedido", "histórico de pedidos"],
    },
    {
        "topico": "ajuda",
        "titulo": "Página Ajuda",
        "conteudo": (
            "A página Ajuda responde dúvidas sobre navegação e "
            "funcionamento do produto CredSim, com um campo de pergunta "
            "livre e botões de perguntas prontas. Dúvidas sobre condições "
            "de crédito específicas ou dados de um pedido devem ir para o "
            "Chat de solicitação ou para o Suporte."
        ),
        "termos": ["dúvida", "perguntas frequentes", "faq", "onde peço ajuda"],
    },
    {
        "topico": "prazo_decisao",
        "titulo": "Quanto tempo demora a aprovação",
        "conteudo": (
            "Nesta demonstração a decisão é imediata: ao clicar em "
            "\"Finalizar solicitação\" com documento, CPF e e-mail "
            "preenchidos, o sistema já retorna o resultado (aprovado ou "
            "reprovado) e, se aprovado, a confirmação da liberação do "
            "dinheiro — tudo na mesma tela, sem fila de análise manual."
        ),
        "termos": ["quanto tempo", "demora", "tempo de espera", "quando sai o resultado"],
    },
]

_RESPOSTA_FALLBACK = (
    "Não tenho uma resposta pronta pra essa pergunta. Posso ajudar com dúvidas "
    "sobre: a página Início, o chat de solicitação (quais dados ele pede e o "
    "que acontece ao final), como simular um empréstimo, as propostas dos "
    "parceiros e como aceitar uma, o envio e a validação de documento, como "
    "finalizar uma solicitação (aprovação e liberação do dinheiro), a "
    "consulta de pedidos no Suporte e o que cada status de solicitação "
    "significa."
)

# Palavras de função em português (artigos, preposições, pronomes...) — sem
# filtrar isso, qualquer pergunta em prosa empataria vários documentos só por
# compartilharem conectores comuns, mascarando o documento certo.
_STOPWORDS = {
    "a", "o", "as", "os", "um", "uma", "uns", "umas", "de", "da", "do", "das",
    "dos", "em", "no", "na", "nos", "nas", "por", "para", "com", "sem", "que",
    "qual", "quais", "como", "onde", "quando", "quem", "cada", "mais", "menos",
    "muito", "pouco", "seu", "sua", "seus", "suas", "meu", "minha", "meus",
    "minhas", "este", "esta", "estes", "estas", "esse", "essa", "esses",
    "essas", "isso", "isto", "aquilo", "ele", "ela", "eles", "elas", "voce",
    "voces", "ao", "aos", "e", "ou", "mas", "se", "nao", "sim", "ja", "ainda",
    "ate", "apos", "depois", "antes", "entre", "sobre", "outro", "outra",
    "outros", "outras", "qualquer", "alguma", "algum", "alguns", "algumas",
    "nenhum", "nenhuma", "sao", "foi", "foram", "ser", "estar", "tem", "ha",
    "posso", "pode", "podem", "preciso", "precisa", "eu", "tu", "vos", "me",
    "te", "lhe", "lhes", "num", "numa", "pelo", "pela", "pelos", "pelas",
    "ai", "la", "aqui", "tambem",
}

_PONTUACAO = string.punctuation


def _normalizar(texto: str) -> str:
    """Remove acentos (NFKD + descarta marcas de combinação) — o cliente nem
    sempre digita acento, e a busca não deveria depender disso pra casar."""
    nfkd = unicodedata.normalize("NFKD", texto or "")
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def _tokens(texto: str) -> set:
    """Tokeniza + normaliza + descarta stopwords/pontuação. Acrescenta também
    uma forma "singularizada" (sem o 's' final) de cada palavra — uma
    de-pluralização ingênua, só pra casar 'documento' com 'documentos' sem
    precisar de um índice de sinônimos pra cada variação de plural."""
    brutas = _normalizar(texto).lower().split()
    limpas = (p.strip(_PONTUACAO) for p in brutas)
    base = {p for p in limpas if len(p) > 2 and p not in _STOPWORDS}
    singularizadas = {p[:-1] for p in base if p.endswith("s") and len(p) > 4}
    return base | singularizadas


def _texto_indexavel(doc: dict) -> str:
    return doc["titulo"] + " " + doc["conteudo"] + " " + " ".join(doc.get("termos", []))


def buscar(pergunta: str, limite: int = 2) -> list:
    """Recuperação mock por interseção de palavras (mesmo estilo de
    `rag.py::search`/`suporte.py::buscar`, sem embeddings de verdade): pontua
    cada documento pelo número de palavras da pergunta que aparecem nele
    (título + conteúdo + termos de apoio) e devolve os `limite` com maior
    pontuação. Sem nenhuma palavra em comum, devolve lista vazia — é o sinal
    pra quem chama cair no fallback."""
    palavras = _tokens(pergunta)
    if not palavras:
        return []

    pontuados = []
    for doc in _BASE:
        pontuacao = len(palavras & _tokens(_texto_indexavel(doc)))
        if pontuacao > 0:
            pontuados.append((pontuacao, doc))

    pontuados.sort(key=lambda item: item[0], reverse=True)
    return [doc for _, doc in pontuados[:limite]]


def _resposta_mock(docs: list) -> str:
    if not docs:
        return _RESPOSTA_FALLBACK
    return " ".join(doc["conteudo"] for doc in docs)


def _contexto_para_ia(docs: list) -> str:
    """Bloco de "notas internas" com o conteúdo recuperado — mesmo padrão de
    `chatbot.py:_contexto_intake_para_ia`: o modelo só FORMULA a resposta em
    cima disso, não pesquisa nem inventa dado novo por conta própria."""
    if not docs:
        return (
            "[NOTAS INTERNAS — não visíveis ao cliente]\n"
            "Nenhum documento da base de conhecimento foi recuperado para "
            "esta pergunta.\n"
            "[FIM DAS NOTAS INTERNAS]\n"
            "Diga educadamente que você não tem essa informação e sugira, "
            "de forma breve, os temas que você cobre (páginas Início, Chat, "
            "Simulação, Documento, Suporte e Ajuda). Não invente uma resposta."
        )
    trechos = "\n".join(f"- {d['titulo']}: {d['conteudo']}" for d in docs)
    return (
        "[NOTAS INTERNAS — não visíveis ao cliente; é a ÚNICA fonte sobre o "
        "app que você deve usar para responder]\n"
        f"{trechos}\n"
        "[FIM DAS NOTAS INTERNAS]\n"
        "Responda à pergunta do cliente com base SOMENTE no conteúdo acima, "
        "em português natural e direto. Se algum detalhe perguntado não "
        "estiver coberto ali, diga que não tem essa informação em vez de "
        "inventar."
    )


def perguntar(pergunta: str) -> dict:
    docs = buscar(pergunta)
    pergunta_reconhecida = bool(docs)

    if config.LLM_MODE == "mock":
        resposta = _resposta_mock(docs)
    else:
        # local/real: RAG de verdade — o(s) documento(s) recuperado(s) vira(m)
        # notas internas na mensagem do usuário, e o modelo só formula a
        # resposta em cima delas (nunca busca nem inventa por conta própria).
        mensagens = [{"role": "user", "content": f"{pergunta}\n\n{_contexto_para_ia(docs)}"}]
        resposta = llm.generate(load("ajuda"), mensagens)

    log_event({
        "scenario": "ajuda", "stage": "resposta",
        "pergunta": pergunta, "pergunta_reconhecida": pergunta_reconhecida,
        "topicos_recuperados": [d["topico"] for d in docs],
    })

    return {
        "pergunta": pergunta,
        "resposta": resposta,
        "pergunta_reconhecida": pergunta_reconhecida,
        "topicos_recuperados": [d["topico"] for d in docs],
    }
