import pdfminer.high_level
from docx import Document
import tempfile
import os

def extract_text(file):
    try:
        if file.name.endswith(".pdf"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(file.read())
                text = pdfminer.high_level.extract_text(tmp.name)
            os.unlink(tmp.name)
            return text
            
        elif file.name.endswith(".docx"):
            doc = Document(file)
            return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
            
        else:
            raise ValueError("Unsupported file type. Please upload PDF or DOCX.")
            
    except Exception as e:
        raise ValueError(f"Error processing file {file.name}: {str(e)}")