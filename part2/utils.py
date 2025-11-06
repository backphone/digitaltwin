import os
from docx import Document
import textract

def load_file_content(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    try:
        if ext == ".txt":
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        elif ext == ".pdf":
            return textract.process(filepath).decode("utf-8", errors="ignore")
        elif ext in [".docx", ".doc"]:
            doc = Document(filepath)
            return "\n".join([para.text for para in doc.paragraphs])
        else:
            return ""  # Skip images, etc.
    except Exception as e:
        print(f"⚠️ Failed to load {filepath}: {e}")
        return ""
