from pathlib import Path


def read_pdf_text(file_path):
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError("Only PDF files are supported.")
    return (
        "PDF preview is not available in this offline desktop version. "
        f"The file was loaded successfully: {path.name}. "
        "Use a PDF viewer or integrate PyMuPDF/pdfplumber for full text extraction."
    )
