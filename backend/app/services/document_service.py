import PyPDF2
import docx
import io

def extract_text_from_file(file_content: bytes, filename: str) -> str:
    """
    Extract text from PDF, DOCX, or TXT files.
    """
    extension = filename.split('.')[-1].lower()
    
    if extension == 'pdf':
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text.strip()
    
    elif extension == 'docx':
        doc = docx.Document(io.BytesIO(file_content))
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text.strip()
    
    elif extension == 'txt':
        return file_content.decode('utf-8').strip()
    
    else:
        raise ValueError(f"Unsupported file extension: {extension}")
