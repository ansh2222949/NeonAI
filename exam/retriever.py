import os
import chromadb
from chromadb.utils import embedding_functions


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(CURRENT_DIR, "vector_store")

EMBEDDING_FUNC = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)


def get_relevant_context(query, n_results=3, collection_name="exam_syllabus", min_score=0.3):
    """
    Searches the Vector DB for text relevant to the query.

    Returns:
        - Clean joined context string
        - OR None if no meaningful match found
    """

    try:
        client = chromadb.PersistentClient(path=DB_DIR)

        # -----------------------------
        # Check if collection exists
        # -----------------------------
        existing_collections = [c.name for c in client.list_collections()]

        if collection_name not in existing_collections:
            print(f"[Retriever] Collection '{collection_name}' not found.")
            return None

        collection = client.get_collection(
            name=collection_name,
            embedding_function=EMBEDDING_FUNC
        )

        # -----------------------------
        # Query Vector DB
        # -----------------------------
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            include=["documents", "distances"]
        )

        if not results or not results.get("documents"):
            return None

        documents = results["documents"][0]
        distances = results.get("distances", [[]])[0]

        if not documents:
            return None

        # -----------------------------
        # Filter Low Quality Matches
        # -----------------------------
        filtered_chunks = []

        for doc, distance in zip(documents, distances):
            if distance is None:
                continue

            # Lower distance = better match
            similarity_score = 1 - distance

            if similarity_score >= min_score:
                filtered_chunks.append(doc.strip())

        if not filtered_chunks:
            return None

        # Remove duplicates
        filtered_chunks = list(dict.fromkeys(filtered_chunks))

        # Clean Join
        clean_context = "\n\n---\n\n".join(filtered_chunks)

        return clean_context

    except Exception as e:
        print(f"[Retriever Error] {e}")
        return None
