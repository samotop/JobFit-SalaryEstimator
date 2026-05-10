import pdfplumber
from docx import Document

def extract_text(file_path: str) -> str:
    if file_path.endswith(".pdf"):
        text = extract_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        text = extract_from_docx(file_path)
    else:
        raise ValueError("Nepodporovaný formát. Použite PDF alebo DOCX.")

    if not text or len(text.strip()) < 100:
        raise ValueError("CV je prázdne alebo obsahuje príliš málo textu. Skontrolujte či súbor nie je skenovaný obrázok.")

    return text.strip()

def extract_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text.strip()

def extract_from_docx(file_path):
    doc = Document(file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text.strip()