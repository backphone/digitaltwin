from flask import Flask, request, jsonify
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from openai import OpenAI
from config.global_config import get_openai_api_key
import os
import json
import PyPDF2

app = Flask(__name__)

# ✅ Load FAISS vectorstore
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-MiniLM-L3-v2")
#result = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
#vectorstore = result[0]

#vectorstore, *_ = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
try:
    vectorstore = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
except Exception as exc:
    vectorstore = None
    print(f"❌ Failed to load FAISS index: {exc}")

# ✅ Initialize OpenAI client
client = OpenAI(api_key=get_openai_api_key())

# ✅ Feedback log paths
FEEDBACK_FILE = "logs/feedback.json"
EXTRACTED_FEEDBACK_DIR = "feedback_chunks"
os.makedirs(EXTRACTED_FEEDBACK_DIR, exist_ok=True)
os.makedirs("logs", exist_ok=True)

# ✅ Feedback helper: Extract text from PDF page
def extract_pdf_page(pdf_path, page_number):
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            if page_number < 1 or page_number > len(reader.pages):
                return None, "Page number out of range."
            text = reader.pages[page_number - 1].extract_text()
            return text.strip() if text else None, None
    except Exception as e:
        return None, f"PDF extraction error: {e}"

# ✅ Feedback saving function
def save_feedback(user_query, correct_doc, correct_page, comment=None):
    extracted_text, error = extract_pdf_page(correct_doc, correct_page)
    if error:
        print(f"❌ {error}")
        return jsonify({"status": "fail", "error": error})

    chunk_filename = f"{os.path.basename(correct_doc).replace('.pdf', '')}_page_{correct_page}.txt"
    chunk_path = os.path.join(EXTRACTED_FEEDBACK_DIR, chunk_filename)
    with open(chunk_path, 'w', encoding='utf-8') as f:
        f.write(extracted_text)

    feedback = {
        "query": user_query,
        "correct_doc": correct_doc,
        "correct_page": correct_page,
        "comment": comment,
        "extracted_chunk": chunk_path
    }
    with open(FEEDBACK_FILE, 'a') as f:
        f.write(json.dumps(feedback) + "\n")
    print(f"✅ Feedback saved and chunk extracted to {chunk_path}")
    return jsonify({"status": "success", "message": "Feedback saved"})


# ✅ Ask endpoint (增强：日志 + 分数 + 可返回debug)
from flask import request, jsonify

@app.route("/ask", methods=["POST"])
def ask():
    # 兼容多个字段名
    data = request.get_json(silent=True) or {}
    prompt = (data.get("prompt") or data.get("query") or data.get("question") or "").strip()
    want_debug = request.args.get("debug") in ("1", "true", "yes")

    if len(prompt) < 2:
        return jsonify({"response": "Please send a non-empty 'prompt' (or 'query'/'question')."}), 200

    if vectorstore is None:
        return jsonify({
            "response": "Vector index not loaded. Run build_faiss_langchain.py before querying.",
            "status": "error"
        }), 503

    print("\n===== User Query =====")
    print(prompt)

    # 🔹1) 检索 + 分数
    try:
        results = vectorstore.similarity_search_with_score(prompt, k=3)
    except Exception as e:
        print("Similarity search error:", e)
        results = []

    print("===== Retrieved Chunks =====")
    debug_chunks = []
    for i, (doc, score) in enumerate(results, 1):
        snippet = (doc.page_content or "")[:300].replace("\n", " ")
        meta = getattr(doc, "metadata", {}) or {}
        print(f"[{i}] Score={score:.4f} | meta={meta}")
        print(snippet + "...\n")
        debug_chunks.append({
            "rank": i,
            "score": float(score),
            "snippet": (doc.page_content or "")[:800],
            "metadata": meta,
        })

    # 🔹2) 组装上下文 & 最终 Prompt
    context = "\n\n".join([doc.page_content for doc, _ in results]) if results else "No relevant content found."
    final_prompt = f"Context:\n{context}\n\nQuestion: {prompt}\nAnswer:"
    print("===== Final Prompt to OpenAI =====")
    print((final_prompt[:1000] + (" ...[truncated]" if len(final_prompt) > 1000 else "")) + "\n")

    # 🔹3) 调用 LLM
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system",
                 "content": "You are a professional maritime support assistant. Use only the given context. "
                            "If info is missing, say you don't know and avoid fabricating."},
                {"role": "user", "content": final_prompt}
            ],
            temperature=0.3,
            max_tokens=800
        )
        answer = resp.choices[0].message.content
    except Exception as e:
        print(f"Error from OpenAI: {e}")
        answer = "Failed to generate response due to an internal error."

    print("===== Model Answer =====")
    print(answer + "\n")

    # 🔹4) 可选：随响应返回 debug
    payload = {"response": answer}
    if want_debug:
        payload["debug"] = {
            "query": prompt,
            "chunks": debug_chunks,
            "final_prompt_preview": final_prompt[:1200],
        }
    return jsonify(payload), 200



# ✅ Feedback endpoint
@app.route('/feedback', methods=['POST'])
def feedback():
    data = request.get_json()
    user_query = data['query']
    correct_doc = data['correct_doc']
    correct_page = int(data['correct_page'])
    comment = data.get('comment', None)

    return save_feedback(user_query, correct_doc, correct_page, comment)

# ✅ Start the Flask server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
