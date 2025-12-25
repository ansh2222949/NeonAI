import os
import shutil
import chromadb
from chromadb.utils import embedding_functions
from pypdf import PdfReader

# --- CONFIGURATION ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(CURRENT_DIR, "uploads")
DB_DIR = os.path.join(CURRENT_DIR, "vector_store")

EMBEDDING_FUNC = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)


def process_pdf(filename="syllabus.pdf"):
    """
    Reads PDF, chunks text, and refreshes the Vector DB.
    """
    pdf_path = os.path.join(UPLOAD_DIR, filename)
    print(f"📄 [Indexer] Processing: {filename}...")

    if not os.path.exists(pdf_path):
        return False, "File not found on server."

    # Read PDF content
    full_text = ""
    try:
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
    except Exception:
        return False, "Error reading PDF. Is it encrypted?"

    # Clean text
    full_text = full_text.replace('\n', ' ').replace('  ', ' ').strip()

    if len(full_text) < 50:
        return False, "PDF content is too short."

    # Create chunks
    chunk_size = 500
    overlap = 50
    chunks = []

    if len(full_text) <= chunk_size:
        chunks.append(full_text)
    else:
        for i in range(0, len(full_text), chunk_size - overlap):
            chunk = full_text[i:i + chunk_size]
            if len(chunk) > 20:
                chunks.append(chunk)

    print(f"🧩 [Indexer] Created {len(chunks)} text chunks.")

    # Update Database
    try:
        client = chromadb.PersistentClient(path=DB_DIR)

        # Remove old collection if exists
        try:
            client.delete_collection(name="exam_syllabus")
            print("🗑️ [Indexer] Old syllabus deleted.")
        except Exception:
            pass

        # Create fresh collection
        collection = client.create_collection(
            name="exam_syllabus",
            embedding_function=EMBEDDING_FUNC
        )

        ids = [f"id_{i}" for i in range(len(chunks))]
        metadatas = [{"source": filename} for _ in chunks]

        collection.add(
            documents=chunks,
            ids=ids,
            metadatas=metadatas
        )

        print("✅ [Indexer] Database Updated Successfully!")
        return True, f"Success! Indexed {len(chunks)} topics."

    except Exception as e:
        print(f"❌ DB Error: {e}")
        return False, f"Database Error: {str(e)}"


def clear_database():
    """
    Resets the Vector DB folder and deletes the uploaded PDF.
    """
    try:
        if os.path.exists(DB_DIR):
            shutil.rmtree(DB_DIR)
            print("🧹 [Indexer] Vector DB Folder Removed.")

        pdf_path = os.path.join(UPLOAD_DIR, "syllabus.pdf")
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
            print("🗑️ [Indexer] PDF File Removed.")

        return True, "Exam Database & PDF Reset Successfully."

    except Exception as e:
        print(f"❌ Clear Error: {e}")
        return False, str(e)
