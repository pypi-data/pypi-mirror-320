import fitz
from io import BytesIO

def read_pdf(pdf_path_or_bytes):
    """
    Extracts text from a PDF file using PyMuPDF.

    Args:
        pdf_path_or_bytes (str or BytesIO): The path to the PDF file or a BytesIO object containing the PDF content.

    Returns:
        str: The extracted text from the PDF.
    """
    try:
        # Open the PDF file or byte stream
        if isinstance(pdf_path_or_bytes, BytesIO):
            document = fitz.open(stream=pdf_path_or_bytes, filetype="pdf")
        else:
            document = fitz.open(pdf_path_or_bytes)

        text = ""
        # Iterate through all the pages
        for page_num in range(len(document)):
            page = document[page_num]
            # Extract text from the page
            text += page.get_text()
        document.close()
        return text
    except Exception as e:
        return f"An error occurred: {e}"

def read_pdf_with_pages(pdf_path_or_bytes):
    """
    Extracts text from a PDF file using PyMuPDF and includes page markers.

    Args:
        pdf_path_or_bytes (str or BytesIO): The path to the PDF file or a BytesIO object containing the PDF content.

    Returns:
        str: The extracted text from the PDF with page markers.
    """
    try:
        # Open the PDF file or byte stream
        if isinstance(pdf_path_or_bytes, BytesIO):
            document = fitz.open(stream=pdf_path_or_bytes, filetype="pdf")
        else:
            document = fitz.open(pdf_path_or_bytes)

        text = ""
        # Iterate through all the pages
        for page_num in range(len(document)):
            page = document[page_num]
            # Extract text from the page and add page markers
            text += f"<|PAGE_START_{page_num+1}|>" + page.get_text() + f"<|PAGE_END_{page_num+1}|>"
        document.close()
        return text
    except Exception as e:
        return f"An error occurred: {e}"
