import openai
import pickle
import json
import time
from sentence_transformers import SentenceTransformer, util

# ========== 配置 ==========
OPENAI_API_KEY = "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"  # 你的OpenAI key
DOC_EMBEDDING_FILE = "doc_embeddings.pkl"  # 步骤1生成的文档embedding
FAQ_FILE = "faq.txt"                      # 你的FAQ文本，每行一个问题
OUTPUT = "qa_knowledge_faq.jsonl"             # 输出jsonl

openai.api_key = OPENAI_API_KEY

# ========== 载入文档embedding ==========
with open(DOC_EMBEDDING_FILE, "rb") as f:
    doc_ids, doc_texts, doc_embeds = pickle.load(f)

# ========== 载入FAQ ==========
with open(FAQ_FILE, "r", encoding="utf-8") as f:
    questions = [line.strip() for line in f if line.strip()]

# ========== 加载embedding模型（和文档embedding保持一致）==========
model = SentenceTransformer("paraphrase-MiniLM-L6-v2")

# ========== 处理 ==========
threshold = 0.15  # 你可以调高到 0.6, 0.7, 取决于实际效果

with open(OUTPUT, "w", encoding="utf-8") as out_f:
    for idx, q in enumerate(questions):
        print(f"🔍 [{idx+1}/{len(questions)}] Q: {q}")
        # 1. embedding
        q_embed = model.encode(q)
        # 2. 找最相似文档
        sim_scores = util.cos_sim(q_embed, doc_embeds)[0]
        top_idx = int(sim_scores.argmax())
        ref_text = doc_texts[top_idx]

        confidence = float(sim_scores[top_idx])

        if confidence < threshold:
            # 置信度低，直接输出“不确定”
            answer = "根据所提供的信息无法确定。"
            print(f"❓ Low confidence ({confidence:.2f}), skipped GPT.")
        else:
            prompt = (
                f"You are a technical support assistant. Read the following reference information, "
                f"and answer the question as accurately and concisely as possible.\n"
                f"Question: {q}\n"
                f"Reference:\n{ref_text[:800]}\n"
                "Answer:"
            )
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2,
                    max_tokens=512
                )
                answer = response["choices"][0]["message"]["content"].strip()
            except Exception as e:
                answer = f"⚠️ AI生成失败: {e}"

        time.sleep(2)

        qa = {
            "question": q,
            "answer": answer,
            "confidence": confidence
        }
        out_f.write(json.dumps(qa, ensure_ascii=False) + "\n")
