from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# 初始化 Embedding 模型
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-MiniLM-L3-v2")

try:
    # 尝试加载 FAISS 索引
    vectorstore = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    print("✅ 成功加载 FAISS 索引")
    print("返回类型:", type(vectorstore))

    # 执行一次简单的相似度搜索
    query = "test query"
    results = vectorstore.similarity_search(query, k=3)

    print(f"🔍 相似度搜索结果（query='{query}'）:")
    for i, doc in enumerate(results):
        print(f"\n--- 第 {i+1} 个结果 ---")
        print(doc.page_content)

except Exception as e:
    print("❌ 出错:", e)

