import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# Paths
FAISS_MAIN_DIR = '/home/ubuntu/ai_env/faiss_index/'
FEEDBACK_FAISS_DIR = '/home/ubuntu/ai_env/feedback_faiss/'
EMBEDDINGS_MODEL = "sentence-transformers/paraphrase-MiniLM-L3-v2"

# Initialize embedding model (MUST match the one used for both)
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDINGS_MODEL)

def merge_faiss_indexes():
    # Load main FAISS index
    main_store = FAISS.load_local(FAISS_MAIN_DIR, embeddings, allow_dangerous_deserialization=True)
    print("✅ Loaded main FAISS index")

    # Load feedback FAISS index
    feedback_store = FAISS.load_local(FEEDBACK_FAISS_DIR, embeddings, allow_dangerous_deserialization=True)
    print("✅ Loaded feedback FAISS index")

    # Merge feedback into main
    main_store.merge_from(feedback_store)
    print("✅ Merged feedback into main index")

    # Save the updated FAISS index back to main
    main_store.save_local(FAISS_MAIN_DIR)
    print(f"✅ Updated FAISS index saved at {FAISS_MAIN_DIR}")

if __name__ == "__main__":
    merge_faiss_indexes()
