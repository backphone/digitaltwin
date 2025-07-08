import os
import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from utils import load_file_content

# 每次重新初始化 FAISS 索引和 metadata 列表
index = faiss.IndexFlatL2(384)  # 或你实际的维度
metadata = []

# 路径配置
#DOC_DIR = "/home/ubuntu/ai_env/documents/AI_Training_Material"
DOC_DIR = "/home/ubuntu/ai_env/documents/AI_Training_Material/test"
INDEX_PATH = "/home/ubuntu/ai_env/faiss_index/index.faiss"
META_PATH = "/home/ubuntu/ai_env/faiss_index/index.pkl"

# 模型和索引初始化
EMBED_MODEL = "all-MiniLM-L6-v2"
embedder = SentenceTransformer(EMBED_MODEL)

# 加载或新建索引和元数据
def load_existing_index(index_path, meta_path):
    if os.path.exists(index_path) and os.path.exists(meta_path):
        print("🟡 Loading existing FAISS index and metadata...")
        index = faiss.read_index(index_path)
        with open(meta_path, "rb") as f:
            metadata = pickle.load(f)
            if isinstance(metadata, tuple):
                metadata = list(metadata)
        return index, metadata
    else:
        print("🟢 Creating new FAISS index...")
        index = faiss.IndexFlatL2(384)
        metadata = []
        return index, metadata

index, metadata = load_existing_index(INDEX_PATH, META_PATH)

# 文本切分,smaller chunk size means higher granuity,
def split_text(text, chunk_size=800, overlap=100):
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

# 文件处理逻辑
def process_file(filepath):
    global metadata
    print(f"🔍 Processing file: {filepath}")
    try:
        content = load_file_content(filepath)
        if not content.strip():
            print(f"⚠️ Skipped (empty file)")
            return

        chunks = split_text(content)
        embeddings = embedder.encode(chunks)

        for i, vec in enumerate(embeddings):
            index.add(np.array([vec]))
            metadata.append({
                "source": f"{filepath} :: chunk {i+1}",
                "text": chunks[i]  # ✅ 添加这一行
        })

    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}")

# 遍历文档目录
for root, _, files in os.walk(DOC_DIR):
    for file in files:
        filepath = os.path.join(root, file)
        process_file(filepath)

# 保存索引和元数据
faiss.write_index(index, INDEX_PATH)
with open(META_PATH, "wb") as f:
    pickle.dump(metadata, f)

print("✅ Processing completed and index saved.")

print(f"🧠 Total chunks saved: {len(metadata)}")

