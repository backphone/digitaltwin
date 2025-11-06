import pickle
from sentence_transformers import SentenceTransformer

# 参数配置
FAQ_TXT = "faq.txt"              # 一行一个 FAQ 问题
EMBEDDINGS_FILE = "faq_embeddings.pkl"
MODEL_NAME = "all-MiniLM-L6-v2"  # 或换成你的 model

# 1. 加载模型
model = SentenceTransformer(MODEL_NAME)

# 2. 读取 FAQ 问题
faq_ids = []
faq_questions = []
with open(FAQ_TXT, "r", encoding="utf-8") as f:
    for idx, line in enumerate(f):
        q = line.strip()
        if q:
            faq_ids.append(f"Q{idx+1}")
            faq_questions.append(q)

# 3. 计算 embedding
faq_embeddings = model.encode(faq_questions, show_progress_bar=True)

# 4. 保存 embedding
with open(EMBEDDINGS_FILE, "wb") as f:
    pickle.dump((faq_ids, faq_questions, faq_embeddings), f)

print(f"✅ Saved {len(faq_questions)} FAQ embeddings to {EMBEDDINGS_FILE}")

