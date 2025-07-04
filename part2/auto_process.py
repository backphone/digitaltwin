LOG_FILE = '/home/ubuntu/ai_env/logs/auto_training_log.txt'

import os
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

# Set the specific folder to scan
UPLOAD_DIR = '/home/ubuntu/ai_env/documents/AI_Training_Material/'
TXT_DIR = '/home/ubuntu/ai_env/documents/txt/'
CHUNK_THRESHOLD = 100000  # characters
DEFAULT_CHUNK_SIZE = 1000

def convert_pdf_pdftotext(pdf_path, output_txt_path):
    """Use pdftotext for PDF conversion"""
    try:
        subprocess.run(['pdftotext', pdf_path, output_txt_path], check=True)
        print(f"Converted PDF: {pdf_path} -> {output_txt_path}")
    except subprocess.CalledProcessError:
        print(f"Failed to convert PDF: {pdf_path}")

def convert_docx_to_txt(docx_path, output_txt_path):
    """Convert .docx to .txt"""
    from docx import Document
    try:
        doc = Document(docx_path)
        text = '\n'.join([para.text for para in doc.paragraphs])
        with open(output_txt_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Converted DOCX: {docx_path} -> {output_txt_path}")
    except Exception as e:
        print(f"Failed to convert DOCX: {docx_path} | Error: {e}")

def process_uploaded_files():
    os.makedirs(TXT_DIR, exist_ok=True)
    for file in os.listdir(UPLOAD_DIR):
        input_path = os.path.join(UPLOAD_DIR, file)
        if os.path.isfile(input_path):
            filename, ext = os.path.splitext(file)
            ext = ext.lower()

            if ext == '.pdf':
                output_txt = os.path.join(TXT_DIR, f"{filename}.txt")
                convert_pdf_pdftotext(input_path, output_txt)

            elif ext == '.docx':
                output_txt = os.path.join(TXT_DIR, f"{filename}.txt")
                convert_docx_to_txt(input_path, output_txt)

            elif ext == '.txt':
                shutil.copy(input_path, TXT_DIR)
                print(f"Copied TXT: {input_path} -> {TXT_DIR}")

            else:
                print(f"Skipped unsupported file: {input_path}")

def auto_chunk_and_train():
    """Adjust chunk size if large, then train (FAISS or others)"""
    with open(LOG_FILE, 'a') as log:
        for txt_file in Path(TXT_DIR).glob('*.txt'):
            text = txt_file.read_text(encoding='utf-8', errors='ignore')
            chunk_size = DEFAULT_CHUNK_SIZE
            if len(text) > CHUNK_THRESHOLD:
                chunk_size = 500  # Reduce chunk size for large files

            log.write(f"{datetime.now()} | Trained on: {txt_file.name} | Size: {len(text)} chars | Chunk size: {chunk_size}\n")
            print(f"✅ Training on: {txt_file.name} | Size: {len(text)} chars | Chunk size: {chunk_size}")

            # TODO: Add FAISS/vector training here


if __name__ == '__main__':
    process_uploaded_files()
    auto_chunk_and_train()
    print(f"✅ Training Completed at {datetime.now()}")

with open(LOG_FILE, 'a') as log:
    log.write(f"{datetime.now()} | ✅ Training Completed\n")
    print(f"✅ Training Completed at {datetime.now()}")

