from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
import os

# 文档目录和嵌入模型
DOC_DIR = "/home/ubuntu/ai_env/documents/AI_Training_Material/test"
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-MiniLM-L3-v2")

# 读取所有txt文件内容（遇到乱码自动跳过）
docs = []
for root, _, files in os.walk(DOC_DIR):
    for file in files:
        if file.endswith(".txt"):
            path = os.path.join(root, file)
            try:
                with open(path, encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    docs.append(content)
            except Exception as e:
                print(f"⚠️ 跳过文件 {path}: {e}")

print(f"📄 加载文本文件数量: {len(docs)}")

# 简单分块处理
chunks = []
chunk_size = 800
overlap = 100
for doc in docs:
    for start in range(0, len(doc), chunk_size - overlap):
        end = min(start + chunk_size, len(doc))
        chunk = doc[start:end]
        if chunk.strip():
            chunks.append(chunk)

print(f"🔹 总分块数: {len(chunks)}")

# 构建并保存向量索引（LangChain格式）
vectorstore = FAISS.from_texts(chunks, embeddings)
vectorstore.save_local("/home/ubuntu/ai_env/faiss_index")
print("✅ 用 LangChain 方式重新保存索引！")
