from sentence_transformers import SentenceTransformer
import os
import pickle

DOCS_DIR = "/home/ubuntu/ai_env/documents/AI_Training_Material/convert_to_jsonl"  # 文档目录
EMBEDDINGS_FILE = "doc_embeddings.pkl"
model = SentenceTransformer('all-MiniLM-L6-v2')

doc_texts = []
doc_ids = []

# 读取所有 txt/pdf
def extract_text(path):
    if path.lower().endswith(".txt"):
        with open(path, encoding="utf-8") as f:
            return f.read()
    elif path.lower().endswith(".pdf"):
        from PyPDF2 import PdfReader
        txt = ""
        try:
            pdf = PdfReader(path)
            for page in pdf.pages:
                t = page.extract_text()
                if t: txt += t + "\n"
        except Exception as e:
            print(f"❌ PDF error: {path} {e}")
        return txt
    return ""

for fn in os.listdir(DOCS_DIR):
    p = os.path.join(DOCS_DIR, fn)
    if fn.lower().endswith((".txt", ".pdf")):
        txt = extract_text(p)
        if txt:
            doc_texts.append(txt)
            doc_ids.append(fn)

# 建立文档块 embedding
embeddings = model.encode(doc_texts, show_progress_bar=True)
with open(EMBEDDINGS_FILE, "wb") as f:
    pickle.dump((doc_ids, doc_texts, embeddings), f)
print(f"Saved embeddings for {len(doc_ids)} files.")
