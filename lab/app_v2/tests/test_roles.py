"""Testes do modelo de papéis (`labcore/roles.py`): `admin1` é a identidade
com acesso irrestrito a qualquer checagem de dono do app, com ou sem defesa
ligada — as outras identidades (`usuario-*`/`empresa-*`) continuam sujeitas
às checagens já existentes, sem nenhuma mudança de comportamento.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from labcore import roles, store
from labcore.scenarios import api_exposta, solicitacoes, suporte

_CLIENTE = {"nome": "João Teste", "renda": 6000, "valor": 20000, "prazo": 24}


# --------------------------------------------------------------- unitários ---

def test_eh_admin_reconhece_apenas_admin1():
    assert roles.eh_admin("admin1") is True
    assert roles.eh_admin("usuario-A") is False
    assert roles.eh_admin("empresa-B") is False
    assert roles.eh_admin("") is False
    assert roles.eh_admin(None) is False


def test_papel_de_deriva_pelo_prefixo_da_identidade():
    assert roles.papel_de("admin1") == "admin"
    assert roles.papel_de("usuario-A") == "usuario"
    assert roles.papel_de("empresa-B") == "empresa"
    assert roles.papel_de("") is None
    assert roles.papel_de(None) is None
    assert roles.papel_de("qualquer-coisa-sem-prefixo-conhecido") is None


# ---------------------------------------------------------- suporte.buscar ---

def test_admin_ve_todas_as_solicitacoes_mesmo_com_defesa_ligada():
    store.reset()
    solicitacoes.criar(dict(_CLIENTE), usuario="usuario-A")
    solicitacoes.criar(dict(_CLIENTE), usuario="usuario-B")

    r = suporte.buscar("João Teste", solicitante="admin1", defense_api_security=True)
    # admin1 não é dono de NENHUMA solicitação, mas continua vendo as duas.
    assert len(r) == 2


# -------------------------------------------------- solicitacoes.aceitar_proposta ---

def test_admin_aceita_proposta_de_solicitacao_de_outro_dono_com_defesa_ligada():
    store.reset()
    solicitacao = solicitacoes.criar(dict(_CLIENTE), usuario="usuario-A")
    proposta_id = solicitacao["propostas"][0]["parceiro_id"]

    atualizado = solicitacoes.aceitar_proposta(
        solicitacao["id"], proposta_id, usuario="admin1", defense_api_security=True,
    )
    assert atualizado["status"] == "aceita"
    assert atualizado["proposta_aceita_id"] == proposta_id


# -------------------------------------------------------- api_exposta.get_conversa ---

def test_admin_acessa_qualquer_conversa_com_defesa_ligada():
    api_exposta.reset()
    r = api_exposta.get_conversa(2, solicitante="admin1", defense_api_security=True)  # conversa 2 é da empresa-B
    assert r["autorizado"] is True
    assert r["status"] == 200
    assert r["dono_real"] == "empresa-B"
