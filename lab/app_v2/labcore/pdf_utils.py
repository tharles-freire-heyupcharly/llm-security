"""Extração de texto de PDF — simula o passo de OCR/extração que, num
produto real, precederia a validação de um documento de identidade (ver
`labcore/scenarios/documento.py`). O parser em si não é a superfície de
ataque didática: ele só devolve o texto extraído; é esse texto que o agente
validador trata como DADO (ou, sem defesa, como comando — LLM01/LLM06).
"""
import io

from pypdf import PdfReader


class PdfInvalidoError(Exception):
    """O arquivo enviado não pôde ser lido como PDF."""


def extrair_texto(conteudo: bytes) -> str:
    try:
        leitor = PdfReader(io.BytesIO(conteudo))
        return "\n".join(pagina.extract_text() or "" for pagina in leitor.pages)
    except Exception as exc:
        raise PdfInvalidoError(f"Não foi possível ler o arquivo como PDF: {exc}") from exc
