import os
import chromadb
from chromadb.utils import embedding_functions

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(CURRENT_DIR, "vector_store")

EMBEDDING_FUNC = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)


def get_relevant_context(query, n_results=2):
    """
    Searches the Vector DB for text relevant to the query.
    Returns: A single string context OR None if DB is missing.
    """
    try:
        client = chromadb.PersistentClient(path=DB_DIR)

        # Check if collection exists before accessing
        existing_collections = [c.name for c in client.list_collections()]

        if "exam_syllabus" not in existing_collections:
            print("⚠️ [Retriever] 'exam_syllabus' collection not found.")
            return None

        collection = client.get_collection(
            name="exam_syllabus",
            embedding_function=EMBEDDING_FUNC
        )

        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )

        if not results or not results["documents"] or not results["documents"][0]:
            return None

        return "\n---\n".join(results["documents"][0])

    except Exception as e:
        print(f"❌ [Retriever] Error: {e}")
        return None
