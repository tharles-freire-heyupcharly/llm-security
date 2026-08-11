"""Gera PDFs mínimos com texto, só para os testes de upload de documento —
usa `reportlab` (dependência só de teste/geração de exemplo, não é chamada
pelo app em runtime; o app só LÊ pdf via `pypdf`, ver labcore/pdf_utils.py).
"""
import io

from reportlab.pdfgen import canvas


def pdf_com_texto(linhas: list) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    y = 800
    for linha in linhas:
        c.drawString(72, y, linha)
        y -= 20
    c.save()
    return buffer.getvalue()
