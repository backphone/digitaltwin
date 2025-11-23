\import json
import os
from typing import Dict, List

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from PyPDF2 import PdfReader

from pathlib import Path

# ========== CONFIG ==========
embedding_model = "sentence-transformers/paraphrase-MiniLM-L3-v2"

# Keep absolute paths unchanged to match existing runtime expectations.
DOC_DIR = "/home/ubuntu/ai_env/documents/AI_Training_Material"
INDEX_DIR = "/home/ubuntu/ai_env/faiss_index"
METADATA_PATH = "/home/ubuntu/ai_env/indexed_docs.json"
# ============================


def load_txt(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def load_pdf(path: Path) -> str:
    text = ""
    try:
        reader = PdfReader(str(path))
        for page in reader.pages:
            text += page.extract_text() or ""
    except Exception as e:
        print(f"⚠️ PDF 解析失败: {path} — {e}")
    return text


def chunk_text(text: str, size: int = 800, overlap: int = 100) -> List[str]:
    chunks: List[str] = []
    for i in range(0, len(text), size - overlap):
        part = text[i : i + size]
        if part.strip():
            chunks.append(part)
    return chunks


def load_metadata() -> Dict[str, Dict]:
    if os.path.exists(METADATA_PATH):
        try:
            with open(METADATA_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as exc:
            print(f"⚠️ 无法读取元数据文件，执行全量重建: {exc}")
    return {}


def save_metadata(metadata: Dict[str, Dict]):
    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)


def collect_documents() -> Dict[str, Dict[str, float]]:
    documents: Dict[str, Dict[str, float]] = {}
    for root, _, files in os.walk(DOC_DIR):
        for name in files:
            path = Path(root) / name
            suffix = path.suffix.lower()
            if suffix not in {".txt", ".pdf"}:
                continue
            stat = path.stat()
            documents[str(path)] = {"mtime": stat.st_mtime, "size": stat.st_size}
    return documents


def load_vectorstore():
    if os.path.exists(INDEX_DIR):
        try:
            embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
            return FAISS.load_local(INDEX_DIR, embeddings, allow_dangerous_deserialization=True)
        except Exception as exc:
            print(f"⚠️ 无法加载现有索引，执行全量重建: {exc}")
    return None


<<<<<<< HEAD
def add_document_chunks(vectorstore: FAISS, path: str) -> List[str]:
=======
def load_document_chunks(path: str) -> List[str]:
>>>>>>> 148bfdc (Handle empty document sets in full FAISS rebuild)
    file_path = Path(path)
    suffix = file_path.suffix.lower()
    if suffix == ".txt":
        text = load_txt(file_path)
    elif suffix == ".pdf":
        print(f"📄 正在处理 PDF: {file_path}")
        text = load_pdf(file_path)
    else:
        return []

    if not text.strip():
        return []

<<<<<<< HEAD
    chunks = chunk_text(text)
=======
    return chunk_text(text)


def load_document_chunks(path: str) -> List[str]:
    file_path = Path(path)
    suffix = file_path.suffix.lower()
    if suffix == ".txt":
        text = load_txt(file_path)
    elif suffix == ".pdf":
        print(f"📄 正在处理 PDF: {file_path}")
        text = load_pdf(file_path)
    else:
        return []

    if not text.strip():
        return []

    return chunk_text(text)


def add_document_chunks(vectorstore: FAISS, path: str) -> List[str]:
    chunks = load_document_chunks(path)
    if not chunks:
        return []

    return vectorstore.add_texts(chunks, metadatas=[{"source": path}] * len(chunks))


def rebuild_full_index():
    print("🔄 未找到旧索引，开始全量构建…")
    documents = collect_documents()

    if not documents:
        print("ℹ️ 未找到可索引的文档，跳过索引构建。")
        save_metadata({})
        return

    embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
    vectorstore = None
    metadata: Dict[str, Dict] = {}
    all_chunks = 0

    for path, meta in documents.items():
        chunks = load_document_chunks(path)
        if not chunks:
            continue

        if vectorstore is None:
            vectorstore = FAISS.from_texts(
                chunks, embeddings, metadatas=[{"source": path}] * len(chunks)
            )
            ids = [vectorstore.index_to_docstore_id[i] for i in range(len(chunks))]
        else:
            ids = vectorstore.add_texts(chunks, metadatas=[{"source": path}] * len(chunks))

        if ids:
            metadata[path] = {"mtime": meta["mtime"], "size": meta["size"], "vector_ids": ids}
            all_chunks += len(ids)

    if vectorstore is None:
        print("ℹ️ 所有文档均为空，跳过索引构建。")
        save_metadata({})
        return

    vectorstore.save_local(INDEX_DIR)
    save_metadata(metadata)

    print(f"📚 文档数量: {len(documents)}")
    print(f"🧩 总分块数: {all_chunks}")
    print("✅ FAISS 索引创建完成！")


def incremental_update():
    existing_metadata = load_metadata()
    current_docs = collect_documents()

    if not existing_metadata or not os.path.exists(INDEX_DIR):
        rebuild_full_index()
        return

    vectorstore = load_vectorstore()
    if vectorstore is None:
        rebuild_full_index()
        return

    added_or_modified = []
    for path, meta in current_docs.items():
        if path not in existing_metadata:
            added_or_modified.append(path)
        else:
            old = existing_metadata[path]
            if meta["mtime"] != old.get("mtime") or meta["size"] != old.get("size"):
                added_or_modified.append(path)

    removed_files = [path for path in existing_metadata if path not in current_docs]

    if not added_or_modified and not removed_files:
        print("ℹ️ 没有检测到新增、修改或删除的文件，索引保持不变。")
        return

    # Remove vectors for deleted files
    for path in removed_files:
        ids = existing_metadata.get(path, {}).get("vector_ids", [])
        if ids:
            vectorstore.delete(ids=ids)
        existing_metadata.pop(path, None)
        print(f"🗑️ 已移除删除的文件: {path}")

    total_new_chunks = 0
    for path in added_or_modified:
        # Remove old vectors for modified files
        old_ids = existing_metadata.get(path, {}).get("vector_ids", [])
        if old_ids:
            vectorstore.delete(ids=old_ids)

        ids = add_document_chunks(vectorstore, path)
        if ids:
            meta = current_docs[path]
            existing_metadata[path] = {"mtime": meta["mtime"], "size": meta["size"], "vector_ids": ids}
            total_new_chunks += len(ids)
            print(f"➕ 已更新文件: {path} | 分块数: {len(ids)}")

    vectorstore.save_local(INDEX_DIR)
    save_metadata(existing_metadata)

    print(f"🧩 新增分块总数: {total_new_chunks}")
    print("✅ 增量更新完成！")

