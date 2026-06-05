import chromadb
from chromadb.utils import embedding_functions
import fitz  
import hashlib
import os
from typing import Optional

chroma_client = chromadb.PersistentClient(path="./chroma_db")
embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)


def get_collection(user_id: int):
    collection_name = f"user_{user_id}"
    return chroma_client.get_or_create_collection(
        name=collection_name,
        embedding_function=embedder
    )


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk.strip())
        start += chunk_size - overlap
    return chunks


def doc_id(source: str, chunk_index: int) -> str:
    raw = f"{source}_{chunk_index}"
    return hashlib.md5(raw.encode()).hexdigest()


async def add_text(user_id: int, text: str, source: str) -> int:
    collection = get_collection(user_id)
    chunks = chunk_text(text)

    if not chunks:
        return 0

    ids = [doc_id(source, i) for i in range(len(chunks))]
    metadatas = [{"source": source, "chunk": i} for i in range(len(chunks))]

    existing = set(collection.get(ids=ids)["ids"])
    new_ids, new_chunks, new_meta = [], [], []
    for i, id_ in enumerate(ids):
        if id_ not in existing:
            new_ids.append(id_)
            new_chunks.append(chunks[i])
            new_meta.append(metadatas[i])

    if new_ids:
        collection.add(documents=new_chunks, ids=new_ids, metadatas=new_meta)

    return len(new_ids)


async def add_pdf(user_id: int, file_path: str, source_name: str) -> int:
    doc = fitz.open(file_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()
    return await add_text(user_id, full_text, source_name)


async def query(user_id: int, question: str, n_results: int = 5) -> tuple[str, list[str]]:
    collection = get_collection(user_id)

    count = collection.count()
    if count == 0:
        return "", []

    results = collection.query(
        query_texts=[question],
        n_results=min(n_results, count)
    )

    docs = results["documents"][0]
    metas = results["metadatas"][0]

    context = "\n\n---\n\n".join(docs)
    sources = list({m["source"] for m in metas})

    return context, sources


async def list_documents(user_id: int) -> list[str]:
    collection = get_collection(user_id)
    if collection.count() == 0:
        return []
    all_items = collection.get()
    sources = list({m["source"] for m in all_items["metadatas"]})
    return sorted(sources)


async def delete_document(user_id: int, source: str) -> int:
    collection = get_collection(user_id)
    all_items = collection.get()
    ids_to_delete = [
        id_ for id_, meta in zip(all_items["ids"], all_items["metadatas"])
        if meta["source"] == source
    ]
    if ids_to_delete:
        collection.delete(ids=ids_to_delete)
    return len(ids_to_delete)


async def clear_all(user_id: int):
    collection_name = f"user_{user_id}"
    chroma_client.delete_collection(collection_name)
