import os
import json
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from PyPDF2 import PdfReader

# Paths
FEEDBACK_FILE = '/home/ubuntu/ai_env/logs/feedback.json'
FAISS_INDEX_DIR = '/home/ubuntu/ai_env/faiss_index/'
EMBEDDINGS_MODEL = "sentence-transformers/paraphrase-MiniLM-L3-v2"
NEW_FEEDBACK_FAISS_DIR = '/home/ubuntu/ai_env/feedback_faiss/'

# Initialize Embedding Model
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDINGS_MODEL)

# Function to extract text again if needed
def extract_pdf_page(pdf_path, page_number):
    try:
        with open(pdf_path, 'rb') as f:
            reader = PdfReader(f)
            if page_number < 1 or page_number > len(reader.pages):
                return None
            return reader.pages[page_number - 1].extract_text().strip()
    except Exception as e:
        print(f"PDF extraction error: {e}")
        return None

# Read and process feedback
def load_feedback_and_extract():
    corrected_chunks = []
    if not os.path.exists(FEEDBACK_FILE):
        print("❌ No feedback file found.")
        return corrected_chunks

    with open(FEEDBACK_FILE, 'r') as f:
        for line in f:
            try:
                fb = json.loads(line)
                # Use extracted chunk if exists
                if os.path.exists(fb['extracted_chunk']):
                    with open(fb['extracted_chunk'], 'r', encoding='utf-8') as chunk_file:
                        corrected_chunks.append(chunk_file.read().strip())
                else:
                    # Fallback: extract from PDF again
                    chunk = extract_pdf_page(fb['correct_doc'], fb['correct_page'])
                    if chunk:
                        corrected_chunks.append(chunk)
            except Exception as e:
                print(f"Skipping bad feedback entry: {e}")
    print(f"✅ Total corrected chunks loaded: {len(corrected_chunks)}")
    return corrected_chunks

# Re-embed feedback chunks into FAISS
def rebuild_feedback_faiss(corrected_chunks):
    if not corrected_chunks:
        print("❌ No corrected data to process.")
        return

    # Create new FAISS index from feedback
    feedback_vectorstore = FAISS.from_texts(corrected_chunks, embeddings)
    feedback_vectorstore.save_local(NEW_FEEDBACK_FAISS_DIR)
    print(f"✅ Feedback FAISS index created at {NEW_FEEDBACK_FAISS_DIR}")

if __name__ == "__main__":
    corrected_chunks = load_feedback_and_extract()
    rebuild_feedback_faiss(corrected_chunks)
