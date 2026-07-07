"""
Batch document ingestion into Qdrant.
Usage: python scripts/ingest_documents.py --dir data/docs/ --topic crop_advisory

Supported formats: .pdf, .txt, .docx
"""
import argparse
import os
import sys
import uuid
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def extract_text_pdf(path: str) -> str:
    import fitz
    doc = fitz.open(path)
    return "\n".join(page.get_text() for page in doc)


def extract_text_txt(path: str) -> str:
    return Path(path).read_text(encoding="utf-8", errors="ignore")


def extract_text_docx(path: str) -> str:
    from docx import Document
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()
        if len(chunk) > 80:
            chunks.append(chunk)
        start = end - overlap
    return chunks


def ingest_file(path: str, topic: str, source: str, collection: str, client, embed_fn) -> int:
    ext = Path(path).suffix.lower()
    if ext == ".pdf":
        text = extract_text_pdf(path)
    elif ext == ".txt":
        text = extract_text_txt(path)
    elif ext == ".docx":
        text = extract_text_docx(path)
    else:
        print(f"  Skipping unsupported format: {ext}")
        return 0

    chunks = chunk_text(text)
    if not chunks:
        print(f"  No usable chunks from {path}")
        return 0

    from qdrant_client.models import PointStruct

    batch_size = 32
    ingested = 0
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        embeddings = embed_fn(batch)
        points = [
            PointStruct(
                id=str(uuid.uuid4()),
                vector=emb,
                payload={"text": chunk, "source": source, "topic": topic},
            )
            for chunk, emb in zip(batch, embeddings)
        ]
        client.upsert(collection_name=collection, points=points)
        ingested += len(points)

    return ingested


def main():
    parser = argparse.ArgumentParser(description="Ingest documents into Qdrant knowledge base")
    parser.add_argument("--dir", required=True, help="Directory containing documents")
    parser.add_argument("--topic", default="general", help="Topic tag (e.g. crop_advisory, disease, scheme)")
    parser.add_argument("--source", default="", help="Source name override")
    parser.add_argument("--ext", default="pdf,txt,docx", help="Comma-separated extensions")
    args = parser.parse_args()

    from core.config import settings
    from qdrant_client import QdrantClient
    from services.embedding_service import get_embeddings_batch

    client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key or None)

    extensions = {f".{e.strip().lstrip('.')}" for e in args.ext.split(",")}
    doc_dir = Path(args.dir)

    if not doc_dir.exists():
        print(f"Directory not found: {doc_dir}")
        sys.exit(1)

    files = [f for f in doc_dir.rglob("*") if f.suffix.lower() in extensions]
    print(f"Found {len(files)} file(s) to ingest.")

    total = 0
    for f in files:
        source = args.source or f.stem
        print(f"  Ingesting: {f.name} (topic={args.topic}, source={source})")
        count = ingest_file(
            str(f), args.topic, source, settings.qdrant_collection, client, get_embeddings_batch
        )
        print(f"    → {count} chunks ingested")
        total += count

    print(f"\nDone. Total chunks: {total}")


if __name__ == "__main__":
    main()
