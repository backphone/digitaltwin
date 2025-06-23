<<<<<<< HEAD
# digitaltwin
=======

# AI Email Assistant – Support Response Engine

## 📌 Purpose

This project builds an AI-powered assistant to help generate email replies in a tone consistent with the support team. It uses:

- 📄 Company documentation and technical manuals
- ✉️ Historical emails (full-text, not redacted)
- ⚙️ A FAISS vector store for fast semantic search
- 🧠 Optional fine-tuning based on personalized message tone

---

## ✅ Completed (Part 1 & 2)

### Part 1: Tone Extraction from Emails
- Extracted original full-text emails from `.pst` file using `libpff`.
- Parsed and saved emails into `.txt` format.
- Generated training data for tone/few-shot examples.
- Verified message structure consistency and saved JSONL format for future fine-tuning.

### Part 2: Document Embedding & Search Engine
- Re-activated prior FAISS-based search engine (`ai_env`).
- Confirmed existing embeddings missing or outdated.
- Rebuilt the FAISS index using uploaded company docs.
- Vector store is now ready for document Q&A integration.

---

## 📂 Folder Structure (Key Files)

ai_env/
├── rebuild_faiss_index.py # Rebuild document vector store
├── merge_and_update_faiss.py # Merge new chunks into FAISS index
├── generate_email_finetune_data.py # Prepare email fine-tune set
├── uploaded_docs/ # (To be re-uploaded) Company documents
├── redacted_emails/ # Redacted email samples
├── fine_tune_emails_original.jsonl # Parsed full-text email dataset
├── faiss_index/ # FAISS vector store (rebuilt)


---

## 🚧 Next Steps

### 🔁 Short-Term
- [ ] Re-upload company documents to `uploaded_docs/`
- [ ] Re-run `rebuild_faiss_index.py` to process and embed them
- [ ] Set up retrieval-based QA endpoint (`query_engine.py`)
- [ ] Verify semantic search works with company knowledge

### 🎯 Mid-Term
- [ ] Integrate tone-based few-shot prompts into email reply generation
- [ ] Optional: Fine-tune LLM on parsed email samples (with JSONL)

---

## 🔐 Security
- Restricted EC2 SSH access to static IP: `129.126.246.235`
- S3 is used as the document/email staging area before processing

---

## ✍️ Author & Maintainer
- Managed on AWS EC2 under Python `ai_env` virtual environment
- GitHub repo: [`your_username/ai-support-assistant`](https://github.com/your_username/ai-support-assistant)


>>>>>>> 7a6c2cb (1st Sync 23 Jun 2025, more info in readme)
