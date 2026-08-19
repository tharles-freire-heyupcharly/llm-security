"""Papéis (roles) das identidades do app — sem autenticação de verdade (é um
lab), a identidade é só uma string que o frontend manda; este módulo decide
o PAPEL dela e se ela é a identidade admin (acesso irrestrito, ignora
qualquer checagem de dono em qualquer lugar do app, com ou sem defesa ligada).
"""

IDENTIDADE_ADMIN = "admin1"

PAPEL_ADMIN = "admin"
PAPEL_USUARIO = "usuario"
PAPEL_EMPRESA = "empresa"


def eh_admin(identidade) -> bool:
    return identidade == IDENTIDADE_ADMIN


def papel_de(identidade) -> str:
    """Deriva o papel a partir do prefixo da identidade — não precisa de
    cadastro, casa com a convenção de nomes já usada no app inteiro."""
    if not identidade:
        return None
    if eh_admin(identidade):
        return PAPEL_ADMIN
    if identidade.startswith("empresa-"):
        return PAPEL_EMPRESA
    if identidade.startswith("usuario-"):
        return PAPEL_USUARIO
    return None


# Matriz de permissões — usada pelo endpoint /api/roles (consumido por uma
# nova página do frontend, "Configuração de Roles", que só EXIBE esta tabela;
# não é enforcement de navegação, é documentação viva da política de acesso.
# Mantenha as chaves em `pagina` EXATAMENTE iguais às da lista `PAGES` do
# frontend (frontend/index.html): home, chat, simulacao, documento, analise,
# suporte, parceiros, interno, ajuda, tecnico — mais "roles" pra esta página nova.
FUNCOES = [
    {"pagina": "home", "nome": "Início", "papeis": ["usuario", "empresa", "admin"]},
    {"pagina": "chat", "nome": "Chat (solicitar empréstimo)", "papeis": ["usuario", "admin"]},
    {"pagina": "simulacao", "nome": "Simulação (minhas solicitações)", "papeis": ["usuario", "admin"]},
    {"pagina": "documento", "nome": "Documento (validar/finalizar)", "papeis": ["usuario", "admin"]},
    {"pagina": "analise", "nome": "Análise (agente SQL/Python)", "papeis": ["admin"]},
    {"pagina": "suporte", "nome": "Suporte (consultar solicitações)", "papeis": ["usuario", "admin"]},
    {"pagina": "parceiros", "nome": "Portal de Parceiros", "papeis": ["empresa", "admin"]},
    {"pagina": "interno", "nome": "Interno (gestão interna)", "papeis": ["admin"]},
    {"pagina": "ajuda", "nome": "Ajuda", "papeis": ["usuario", "empresa", "admin"]},
    {"pagina": "tecnico", "nome": "Painel técnico", "papeis": ["admin"]},
    {"pagina": "roles", "nome": "Configuração de Roles", "papeis": ["admin"]},
]
