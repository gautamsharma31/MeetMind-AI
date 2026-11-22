import re

from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import chromadb

CHROMA_DIR = "vector_db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def _collection_name(meeting_id: str) -> str:
    """Create a valid, deterministic Chroma collection name for one meeting."""
    safe_id = re.sub(r"[^a-zA-Z0-9_-]", "", str(meeting_id))
    if not safe_id:
        raise ValueError("A valid meeting ID is required for its vector collection.")
    return f"meeting_{safe_id}"


def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
    )


def build_vector_store(transcript: str, meeting_id: str) -> Chroma:
    """Build an isolated vector collection for this meeting only."""
    if not transcript or not transcript.strip():
        raise ValueError("Cannot build a vector store from an empty transcript.")

    collection_name = _collection_name(meeting_id)
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    # Rebuilding a meeting's RAG index should replace, not duplicate, its chunks.
    try:
        client.delete_collection(name=collection_name)
    except Exception:
        pass

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
    )
    chunks = splitter.split_text(transcript)
    docs = [
        Document(page_content=chunk, metadata={"chunk_index": i, "meeting_id": str(meeting_id)})
        for i, chunk in enumerate(chunks)
    ]

    return Chroma.from_documents(
        documents=docs,
        embedding=get_embeddings(),
        collection_name=collection_name,
        persist_directory=CHROMA_DIR,
    )


def load_vector_store(meeting_id: str) -> Chroma:
    """Load only the vector collection belonging to the requested meeting."""
    return Chroma(
        collection_name=_collection_name(meeting_id),
        embedding_function=get_embeddings(),
        persist_directory=CHROMA_DIR,
    )


def delete_vector_store(meeting_id: str) -> None:
    """Permanently remove one meeting's Chroma collection, if it exists."""
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection_name = _collection_name(meeting_id)
    try:
        client.delete_collection(name=collection_name)
    except Exception as exc:
        # Missing collection is fine; other errors should be reported to the caller.
        if "does not exist" not in str(exc).lower() and "not found" not in str(exc).lower():
            raise


def get_retriever(vector_store: Chroma, k: int = 4):
    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k},
    )
