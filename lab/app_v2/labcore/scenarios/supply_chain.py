"""Supply Chain (LLM03, Aula 2) — modelo comprometido por terceiros.

O hash "confiável" abaixo é o hash REAL do `llama3.2:3b` (Q4_K_M — o modelo
usado no modo `local` deste app), não uma string inventada. Verificado em
11/08/2026 de três formas independentes: sha256 do arquivo de pesos dentro do
container `ollama`, manifesto salvo pelo próprio Ollama ao baixar o modelo, e
a API pública do registro (`registry.ollama.ai`, consulta ao vivo, sem
cache). As três bateram, byte a byte — é esse valor que vira HASH_OFICIAL.

O Ollama repacota em GGUF o release oficial da Meta (huggingface.co/meta-llama);
FONTE_OFICIAL aponta pra página do Ollama, que é de onde este app de fato
baixa o modelo (ver OLLAMA_MODEL no .env). Se a tag `llama3.2:3b` for
atualizada no registro (nova versão do modelo), HASH_OFICIAL precisa ser
revalidado contra a fonte — ele não se atualiza sozinho.
"""

MODELO_VERIFICADO = "llama3.2:3b"
FONTE_OFICIAL = "https://ollama.com/library/llama3.2:3b"
HASH_OFICIAL = "dde5aa3fc5ffc17176b5e8bdc82f587b24b2678c6c66101bf7da77af9f7ccdff"

# Hash que um arquivo ADULTERADO produziria — só pra contrastar com o
# oficial acima; não é o hash de nenhum binário real (ver conversa com o
# autor sobre não baixar/linkar malware de verdade pra este exemplo).
_HASH_ADULTERADO_SIMULADO = "1a2b3c4d5e6f7089fedcba9876543210aabbccddeeff00112233445566778899"

_ORIGENS = {"confiavel": HASH_OFICIAL, "adulterado": _HASH_ADULTERADO_SIMULADO}


def verificar(origem: str = "adulterado") -> dict:
    origem = origem if origem in _ORIGENS else "adulterado"
    obtido = _ORIGENS[origem]
    return {
        "origem": origem,
        "modelo": MODELO_VERIFICADO,
        "fonte_oficial": FONTE_OFICIAL,
        "hash_esperado": HASH_OFICIAL,
        "hash_obtido": obtido,
        "confiavel": obtido == HASH_OFICIAL,
    }
