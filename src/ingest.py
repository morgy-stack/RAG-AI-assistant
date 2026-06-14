from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import chromadb

# =========================
# Load PDF
# =========================
reader = PdfReader("papers/rag.pdf")

text = ""

for page in reader.pages:
    page_text = page.extract_text()

    if page_text:
        text += page_text + "\n"

# =========================
# Chunking
# =========================
chunk_size = 1000
chunk_overlap = 200

chunks = []

for i in range(0, len(text), chunk_size - chunk_overlap):
    chunk = text[i:i + chunk_size]

    if len(chunk.strip()) > 100:
        chunks.append(chunk)

print(f"Created {len(chunks)} chunks")

# =========================
# Embedding Model
# =========================
model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

embeddings = model.encode(
    chunks,
    show_progress_bar=True
).tolist()

# =========================
# ChromaDB
# =========================
client = chromadb.PersistentClient(
    path="./chromadb"
)

# Delete old collection
try:
    client.delete_collection("papers")
except:
    pass

collection = client.create_collection(
    "papers"
)

ids = [str(i) for i in range(len(chunks))]

collection.add(
    ids=ids,
    documents=chunks,
    embeddings=embeddings
)

print("\nDone!")
print(f"Stored {len(chunks)} chunks")