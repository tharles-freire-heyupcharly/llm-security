"""Gera PDFs mínimos com texto, só para os testes de upload de documento —
usa `reportlab` (dependência só de teste/geração de exemplo, não é chamada
pelo app em runtime; o app só LÊ pdf via `pypdf`, ver labcore/pdf_utils.py).
"""
import io

from reportlab.lib.pagesizes import letter
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


def _campo(c, x, y, rotulo, valor):
    c.setFont("Helvetica-Bold", 9)
    c.drawString(x, y, rotulo)
    c.setFont("Helvetica", 11)
    c.drawString(x, y - 14, valor)


def pdf_documento_cliente(
    nome, cpf, rg, nascimento, filiacao, orgao_emissor,
    endereco, cidade_uf, cep, instrucao_oculta=None,
) -> bytes:
    """PDF com aparência de dois documentos reais de KYC (comprovante de
    endereço + carteira de identidade) — em vez do dump de texto cru anterior
    (linhas soltas tipo "extração OCR"). Continua sendo só texto/formas
    vetoriais (reportlab), nada de imagem escaneada de verdade — mas já
    parece um documento composto, não uma lista de campos.

    Tudo é claramente FICTÍCIO/didático (nomes, CPF, RG, endereço, empresa de
    energia — nenhum dado real), rotulado como exemplo em cada seção, pra não
    passar por um documento oficial de verdade.

    `instrucao_oculta`, se informado, é anexado como uma "observação da
    digitalização" ao final — VISÍVEL no texto extraído de propósito (a
    injeção de verdade seria invisível ao olho humano — texto branco sobre
    fundo branco, camada oculta do PDF — aqui fica visível só para fins
    didáticos, ver `exemplos/README.md`).
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    largura, altura = letter

    c.setFillColorRGB(0.85, 0.1, 0.1)
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(largura / 2, altura - 30, "DOCUMENTO FICTÍCIO — EXEMPLO DIDÁTICO (CredSim / Aula de Segurança para LLMs)")
    c.setFillColorRGB(0, 0, 0)

    # --- Comprovante de endereço ---
    topo1 = altura - 60
    c.rect(50, topo1 - 150, largura - 100, 150)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(65, topo1 - 25, "LUZ & ÁGUA FICTÍCIA S.A.")
    c.setFont("Helvetica", 9)
    c.drawString(65, topo1 - 40, "Fatura de exemplo — comprovante de endereço (documento fictício)")
    c.line(65, topo1 - 48, largura - 65, topo1 - 48)
    _campo(c, 65, topo1 - 70, "TITULAR", nome)
    _campo(c, 65, topo1 - 100, "ENDEREÇO", f"{endereco}, {cidade_uf}, CEP {cep}")
    _campo(c, 65, topo1 - 130, "REFERÊNCIA", "fatura de exemplo — uso didático")

    # --- Carteira de identidade ---
    topo2 = topo1 - 170
    c.rect(50, topo2 - 170, largura - 100, 170)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(65, topo2 - 25, "CARTEIRA DE IDENTIDADE (exemplo fictício)")
    c.line(65, topo2 - 33, largura - 65, topo2 - 33)
    _campo(c, 65, topo2 - 55, "NOME", nome)
    _campo(c, 65, topo2 - 85, "RG", rg)
    _campo(c, 300, topo2 - 85, "CPF", cpf)
    _campo(c, 65, topo2 - 115, "DATA DE NASCIMENTO", nascimento)
    _campo(c, 300, topo2 - 115, "ÓRGÃO EMISSOR", orgao_emissor)
    _campo(c, 65, topo2 - 145, "FILIAÇÃO", filiacao)

    if instrucao_oculta:
        y_obs = topo2 - 190
        c.setFont("Helvetica-Oblique", 9)
        c.drawString(65, y_obs, "Observações da digitalização:")
        texto = c.beginText(65, y_obs - 14)
        texto.setFont("Helvetica-Oblique", 9)
        for linha in instrucao_oculta:
            texto.textLine(linha)
        c.drawText(texto)

    c.save()
    return buffer.getvalue()
