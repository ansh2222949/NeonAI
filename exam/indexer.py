import os
import shutil
import chromadb
import re
from chromadb.utils import embedding_functions
from pypdf import PdfReader


# --- CONFIGURATION ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(CURRENT_DIR, "uploads")
DB_DIR = os.path.join(CURRENT_DIR, "vector_store")

EMBEDDING_FUNC = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)


def process_pdf(filename="syllabus.pdf", collection_name="exam_syllabus"):
    """
    Reads PDF, chunks text safely, and refreshes the Vector DB.
    Fully isolated collection per mode.
    """

    pdf_path = os.path.join(UPLOAD_DIR, filename)
    print(f"[Indexer] Processing: {filename}...")

    if not os.path.exists(pdf_path):
        return False, "File not found on server."

    # -----------------------------
    # Read PDF
    # -----------------------------
    full_text = ""

    try:
        reader = PdfReader(pdf_path)

        if reader.is_encrypted:
            return False, "PDF is encrypted."

        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"

    except Exception as e:
        return False, f"Error reading PDF: {str(e)}"

    # -----------------------------
    # Clean Text
    # -----------------------------
    full_text = re.sub(r"\s+", " ", full_text).strip()

    if len(full_text) < 50:
        return False, "PDF content is too short."

    # -----------------------------
    # Smart Chunking (Sentence Safe)
    # -----------------------------
    chunk_size = 500
    overlap = 75
    chunks = []

    start = 0
    text_length = len(full_text)

    while start < text_length:
        end = start + chunk_size

        if end < text_length:
            # Try to end chunk at sentence boundary
            sentence_end = full_text.rfind(".", start, end)
            if sentence_end != -1:
                end = sentence_end + 1

        chunk = full_text[start:end].strip()

        if len(chunk) > 30:
            chunks.append(chunk)

        start = end - overlap

    # Remove duplicates
    chunks = list(dict.fromkeys(chunks))

    print(f"[Indexer] Created {len(chunks)} clean text chunks.")

    # -----------------------------
    # Update Database
    # -----------------------------
    try:
        os.makedirs(DB_DIR, exist_ok=True)

        client = chromadb.PersistentClient(path=DB_DIR)

        # Delete old collection
        try:
            client.delete_collection(name=collection_name)
            print("[Indexer] Old collection deleted.")
        except Exception:
            pass

        # Create new collection
        collection = client.create_collection(
            name=collection_name,
            embedding_function=EMBEDDING_FUNC
        )

        ids = [f"{collection_name}_{i}" for i in range(len(chunks))]
        metadatas = [{"source": filename, "mode": "exam"} for _ in chunks]

        collection.add(
            documents=chunks,
            ids=ids,
            metadatas=metadatas
        )

        print("[Indexer] Database Updated Successfully!")
        return True, f"Success! Indexed {len(chunks)} topics."

    except Exception as e:
        print(f"[DB Error] {e}")
        return False, f"Database Error: {str(e)}"


def clear_database(collection_name="exam_syllabus"):
    """
    Resets the Vector DB folder and deletes the uploaded PDF.
    """

    try:
        client = chromadb.PersistentClient(path=DB_DIR)

        try:
            client.delete_collection(name=collection_name)
            print("[Indexer] Collection removed.")
        except Exception:
            pass

        if os.path.exists(DB_DIR) and not os.listdir(DB_DIR):
            shutil.rmtree(DB_DIR)
            print("[Indexer] Empty DB folder removed.")

        pdf_path = os.path.join(UPLOAD_DIR, "syllabus.pdf")
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
            print("[Indexer] PDF File Removed.")

        return True, "Exam Database & PDF Reset Successfully."

    except Exception as e:
        print(f"[Clear Error] {e}")
        return False, str(e)
