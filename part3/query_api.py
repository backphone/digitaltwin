from flask import Flask, request, jsonify
import numpy as np
import faiss
import traceback

# ⛳️ Replace with your actual embedding model and data
from sentence_transformers import SentenceTransformer

# Assumes index and documents are preloaded
# e.g., loaded from a file or generated at runtime
# Ensure the following objects are defined before starting the server

# Example only:
# index = faiss.IndexFlatL2(384)
# documents = ["doc1 content...", "doc2 content...", ...]
# embedder = SentenceTransformer('all-MiniLM-L6-v2')

# If you load from a file:
# with open("documents.pkl", "rb") as f:
#     documents = pickle.load(f)
# faiss.read_index("vector.index")

app = Flask(__name__)

# Make sure these are initialized properly in your actual code
index = None
documents = []
embedder = None

@app.route("/ask", methods=["POST"])
def ask():
    global index, documents, embedder

    data = request.json
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"answer": "Question is empty."}), 400

    print(f"❓ Question received: {question}")

    try:
        # Step 1: Generate embedding
        query_embedding = embedder.encode([question])
        print(f"🔢 Query embedding shape: {np.array(query_embedding).shape}")

        # Step 2: FAISS search
        D, I = index.search(np.array(query_embedding), k=10)
        print("🔍 FAISS returned indices:", I[0])
        print("📐 FAISS distances:", D[0])

        # Step 3: Retrieve matched documents
        matched_docs = []
        for idx in I[0]:
             if idx == -1:
                continue  # 忽略无效索引（-1 表示未匹配到有效结果）

             if idx < len(documents):
                chunk = documents[idx]
                matched_docs.append(chunk["text"])
                print(f"✅ Match index {idx}: {chunk['text'][:150].replace(chr(10), ' ')}")
             else:
                print(f"⚠️ Invalid index returned by FAISS: {idx}")


        if not matched_docs:
            return jsonify({"answer": "Sorry, I could not find relevant documents."})

        # Step 4: Assemble response (for now just join top 3 chunks)
        response = "\n---\n".join(matched_docs[:3])
        return jsonify({"answer": response})

    except Exception as e:
        print("🔥 Exception in /ask route:")
        traceback.print_exc()
        return jsonify({"answer": f"Internal error: {str(e)}"}), 500

@app.route("/status", methods=["GET"])
def status():
    return jsonify({
        "status": "ok",
        "documents_loaded": len(documents),
        "index_size": index.ntotal if index else 0
    })

if __name__ == "__main__":
    from pathlib import Path
    import pickle

    # 🧠 Load your FAISS index, documents and model here
    print("🔄 Loading FAISS index and documents...")

    embedder = SentenceTransformer('all-MiniLM-L6-v2')

    # Load documents list (replace with your actual path)
    meta_path = Path("/home/ubuntu/ai_env/faiss_index/index.pkl")
    if meta_path.exists():
        with open(meta_path, "rb") as f:
            documents = pickle.load(f)  # 这里是一个包含 dict 的列表，每个 dict 有 'text' 和 'source'
        print(f"✅ Loaded {len(documents)} metadata chunks.")
    else:
        print(f"⚠️ Metadata file not found at {meta_path}")

    # Load FAISS index
    index_path = Path("/home/ubuntu/ai_env/faiss_index/index.faiss")

    if index_path.exists():
        index = faiss.read_index(str(index_path))
        print(f"✅ Loaded FAISS index with {index.ntotal} vectors.")
    else:
        print(f"⚠️ FAISS index not found at {index_path}")

    app.run(host="0.0.0.0", port=5000)
