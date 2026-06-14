import os
from dotenv import load_dotenv

import chromadb
from sentence_transformers import SentenceTransformer
import google.generativeai as genai

# =========================
# Load Environment Variables
# =========================
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found in .env"
    )

# =========================
# Configure Gemini
# =========================
genai.configure(api_key=API_KEY)

model_gemini = genai.GenerativeModel(
    "gemini-2.5-flash"
)

# =========================
# ChromaDB
# =========================
client = chromadb.PersistentClient(
    path="./chromadb"
)

collection = client.get_collection(
    "papers"
)

# =========================
# Embedding Model
# =========================
embed_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

# =========================
# Ask Question
# =========================
question = input("\nAsk a question: ")

# =========================
# Embed Question
# =========================
query_embedding = embed_model.encode(
    question
).tolist()

# =========================
# Retrieve Chunks
# =========================
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=5
)

retrieved_chunks = results["documents"][0]

context = "\n\n".join(retrieved_chunks)

# =========================
# Prompt
# =========================
prompt = f"""
You are a helpful research paper assistant.

Use ONLY the provided context.

If the context contains enough information,
generate a concise answer.

If the context contains partial information,
combine the retrieved information and provide
the best possible answer.

Only say:

"I could not find that information in the uploaded papers."

when the context is completely unrelated.

CONTEXT:
{context}

QUESTION:
{question}
"""

# =========================
# Generate Answer
# =========================
response = model_gemini.generate_content(
    prompt
)

# =========================
# Output
# =========================
print("\n" + "=" * 60)
print("ANSWER")
print("=" * 60)

print(response.text)

print("\n" + "=" * 60)
print("SOURCE CHUNKS")
print("=" * 60)

for i, chunk in enumerate(
    retrieved_chunks,
    start=1
):
    print(f"\nSource {i}")
    print("-" * 50)
    print(chunk[:500])