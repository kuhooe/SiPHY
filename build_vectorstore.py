# 🏗️ build_vectorstore.py — Build Clause Embedding Index

import os
import json
import numpy as np
import faiss
from dotenv import load_dotenv
from openai import OpenAI
from utils import num_tokens
from constants import OPENAI_MODEL

# Load environment
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load clause metadata
with open("metadata.json", "r", encoding="utf-8") as f:
    CLAUSE_METADATA = json.load(f)

# ✂️ Token-limited input builder (800 tokens max)
def truncate_text(text, max_tokens=800):
    tokens = text.split()
    return " ".join(tokens[:max_tokens])

# 🧠 Generate clause embeddings from metadata content
def build_embeddings():
    texts = [
        truncate_text(
            f"{entry['title']} {entry['summary']} {entry.get('external_context', '')}",
            max_tokens=800
        )
        for entry in CLAUSE_METADATA
    ]
    embeddings = []
    for i, text in enumerate(texts):
        response = client.embeddings.create(input=[text], model=OPENAI_MODEL)
        embeddings.append(response.data[0].embedding)
    return np.array(embeddings, dtype="float32")

# 💾 Save FAISS vectorstore
def save_vectorstore():
    os.makedirs("vectorstore", exist_ok=True)
    embeddings = build_embeddings()
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    faiss.write_index(index, "vectorstore/faiss.index")
    np.save("vectorstore/clause_embeddings.npy", embeddings)
    print("✅ Vectorstore saved.")

# 🔧 Script Entry Point
if __name__ == "__main__":
    save_vectorstore()
