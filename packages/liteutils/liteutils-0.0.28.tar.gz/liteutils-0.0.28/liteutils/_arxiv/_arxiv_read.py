
import requests
from io import BytesIO

from liteutils import read_pdf


def read_arxiv(id_or_link: str):
    try:
        id_or_link = id_or_link.replace("/abs/","/pdf/")
        id_or_link = id_or_link.replace("/html/","/pdf/")
        if 'https' not in id_or_link:
            id_or_link = f"https://arxiv.org/pdf/{id_or_link}"
        response = requests.get(id_or_link)
        pdf_content = BytesIO(response.content)
        pdf_text = read_pdf(pdf_content)
    except:
        pdf_text = ""
    return pdf_text

