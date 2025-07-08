from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-MiniLM-L3-v2")

try:
    result = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    print("✅ 成功加载 FAISS")
    print("类型:", type(result))
    if isinstance(result, (list, tuple)):
        print("📦 是元组，长度:", len(result))
        for i, item in enumerate(result):
            print(f"🔹 第{i+1}项类型:", type(item))
    else:
        print("📄 单一对象类型:", type(result))
except Exception as e:
    print("❌ 出错:", e)
