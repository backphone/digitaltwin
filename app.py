from flask import Flask, request, jsonify
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from openai import OpenAI
import os
import json
import PyPDF2

app = Flask(__name__)

# ✅ Load FAISS vectorstore
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-MiniLM-L3-v2")
#result = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
#vectorstore = result[0]

#vectorstore, *_ = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
vectorstore = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)

# ✅ Initialize OpenAI client
client = OpenAI(api_key="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")

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

# ✅ Ask endpoint
@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    prompt = data.get("prompt", "")

    # Retrieve from FAISS
    retrieved_docs = vectorstore.similarity_search(prompt, k=3)
    print("Retrieved docs:", retrieved_docs)

    context = "\n".join([doc.page_content for doc in retrieved_docs]) if retrieved_docs else "No relevant content found."

    # GPT call with clearer instruction
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional support assistant. Using the knowledge below, please answer the user's question clearly and fluently. Reorganize and rephrase if needed to ensure the answer is complete and natural.If the context is fragmented or from multiple files, summarize and rewrite it in a coherent and user-friendly way."
                },
                {"role": "system", "content": context},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,  # 或更大值，例如 1200
            temperature=0.3
        )
        answer = response.choices[0].message.content
    except Exception as e:
        print(f"Error from OpenAI: {e}")
        answer = "Failed to generate response due to an internal error."

    return jsonify({"response": answer})

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
