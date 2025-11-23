import os
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from PyPDF2 import PdfReader

# ========== CONFIG ==========
DOC_DIR = "/home/ubuntu/ai_env/documents/AI_Training_Material"
embedding_model = "sentence-transformers/paraphrase-MiniLM-L3-v2"
# ============================

embeddings = HuggingFaceEmbeddings(model_name=embedding_model)

def load_txt(path: Path):
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except:
        return ""

def load_pdf(path: Path):
    text = ""
    try:
        reader = PdfReader(str(path))
        for page in reader.pages:
            text += page.extract_text() or ""
    except Exception as e:
        print(f"⚠️ PDF 解析失败: {path} — {e}")
    return text

def chunk_text(text, size=800, overlap=100):
    chunks = []
    for i in range(0, len(text), size - overlap):
        part = text[i:i+size]
        if part.strip():
            chunks.append(part)
    return chunks


all_chunks = []
file_count = 0

for root, _, files in os.walk(DOC_DIR):
    for name in files:
        path = Path(root) / name
        suffix = path.suffix.lower()

        file_count += 1

        if suffix == ".txt":
            text = load_txt(path)
        elif suffix == ".pdf":
            print(f"📄 正在处理 PDF: {path}")
            text = load_pdf(path)
        else:
            continue

        if not text.strip():
            continue

        chunks = chunk_text(text)
        all_chunks.extend(chunks)

print(f"📚 文档数量: {file_count}")
print(f"🧩 总分块数: {len(all_chunks)}")

# Build FAISS index
vectorstore = FAISS.from_texts(all_chunks, embeddings)
vectorstore.save_local("/home/ubuntu/ai_env/faiss_index")

print("✅ FAISS 索引创建完成！")
