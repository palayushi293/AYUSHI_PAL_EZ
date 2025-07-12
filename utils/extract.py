import fitz  # type: ignore # PyMuPDF

def extract_text(filepath, file_type):
    if file_type == 'pdf':
        text = ""
        with fitz.open(filepath) as doc:
            for page in doc:
                text += page.get_text()
        return text.strip()
    elif file_type == 'txt':
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read().strip()
    else:
        return ""
