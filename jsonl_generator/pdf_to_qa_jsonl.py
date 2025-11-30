import os
import sys
from pathlib import Path
from PyPDF2 import PdfReader
import openai
import json

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from config.global_config import get_openai_api_key

# ========== 基本参数 ==========
FOLDER = os.path.expanduser("~/ai_env/documents/AI_Training_Material/convert_to_jsonl")
OUTPUT = "qa_knowledge.jsonl"
openai.api_key = get_openai_api_key()

CHUNK_PAGE_SIZE = 2   # 每几页为一块生成一个 Q&A
CHUNK_CHAR_SIZE = 1800  # TXT 文件每多少字符一块

# ========== 工具函数 ==========
def extract_chunks_from_pdf(pdf_path, chunk_page_size=CHUNK_PAGE_SIZE):
    """把 PDF 拆成若干 chunk，每 chunk 多页"""
    chunks = []
    try:
        reader = PdfReader(pdf_path)
        pages = reader.pages
        total = len(pages)
        for i in range(0, total, chunk_page_size):
            chunk_text = ""
            for j in range(i, min(i+chunk_page_size, total)):
                page_text = pages[j].extract_text() or ""
                chunk_text += f"\n[Page {j+1}]\n" + page_text
            if chunk_text.strip():
                chunks.append(chunk_text.strip())
            # 每10页报告一次进度
            if i % 10 == 0:
                print(f"📖 Progress: processed page {i+1}/{total} of {os.path.basename(pdf_path)}")
    except Exception as e:
        print(f"❌ Error reading PDF {pdf_path}: {e}")
    return chunks

def extract_chunks_from_txt(txt_path, chunk_char_size=CHUNK_CHAR_SIZE):
    """把 TXT 拆成若干 chunk，每 chunk 固定字符数"""
    chunks = []
    try:
        with open(txt_path, "r", encoding="utf-8") as f:
            content = f.read()
        for i in range(0, len(content), chunk_char_size):
            chunk = content[i:i+chunk_char_size].strip()
            if chunk:
                chunks.append(chunk)
    except Exception as e:
        print(f"❌ Error reading TXT {txt_path}: {e}")
    return chunks

def gpt_generate_qa(text, max_tokens=1024):
    prompt = (
        "You are a technical support assistant. "
        "Read the following technical documentation chunk, and extract a concise question and answer pair that summarizes the core issue, error, or troubleshooting procedure. "
        "Return your answer in this JSON format: {\"question\": \"...\", \"answer\": \"...\"}\n\n"
        "Documentation:\n"
        f"{text}\n"
        "----\n"
        "Q&A:"
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",   # 或 "gpt-4o"
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=max_tokens
        )
        answer = response["choices"][0]["message"]["content"]
        # 提取 JSON
        json_start = answer.find('{')
        json_end = answer.rfind('}') + 1
        qa = json.loads(answer[json_start:json_end])
        return qa
    except Exception as e:
        print(f"❌ GPT生成失败: {e}")
        return None

# ========== 主程序 ==========
if __name__ == "__main__":
    all_qas = []
    files = [f for f in os.listdir(FOLDER) if f.lower().endswith((".pdf", ".txt"))]
    print(f"📂 文件总数: {len(files)}")

    for file in files:
        path = os.path.join(FOLDER, file)
        print(f"\n📄 正在处理: {file}")
        # 处理 PDF
        if file.lower().endswith(".pdf"):
            chunks = extract_chunks_from_pdf(path)
        # 处理 TXT
        else:
            chunks = extract_chunks_from_txt(path)
        print(f" - 分块数: {len(chunks)}")

        for idx, chunk in enumerate(chunks):
            qa = gpt_generate_qa(chunk)
            if qa:
                # 加入元数据便于追溯
                qa["source"] = file
                qa["chunk_id"] = idx+1
                all_qas.append(qa)

    # 保存结果
    with open(OUTPUT, "w", encoding="utf-8") as f:
        for qa in all_qas:
            f.write(json.dumps(qa, ensure_ascii=False) + "\n")

    print(f"\n🎉 全部完成，共生成 {len(all_qas)} 条 Q&A，结果保存在 {OUTPUT}")
