"""
Run once to create the Qdrant collection for agri knowledge base.
Usage: python scripts/setup_qdrant.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, HnswConfigDiff

from core.config import settings


def main():
    client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key or None)

    collections = {c.name for c in client.get_collections().collections}

    if settings.qdrant_collection in collections:
        print(f"Collection '{settings.qdrant_collection}' already exists.")
        info = client.get_collection(settings.qdrant_collection)
        print(f"  Vectors count: {info.vectors_count}")
        return

    # paraphrase-multilingual-mpnet-base-v2 produces 768-dim vectors
    client.create_collection(
        collection_name=settings.qdrant_collection,
        vectors_config=VectorParams(size=768, distance=Distance.COSINE),
        hnsw_config=HnswConfigDiff(m=16, ef_construct=100),
    )

    # Payload indexes for fast filtering
    client.create_payload_index(
        collection_name=settings.qdrant_collection,
        field_name="topic",
        field_schema="keyword",
    )
    client.create_payload_index(
        collection_name=settings.qdrant_collection,
        field_name="source",
        field_schema="keyword",
    )

    print(f"Created collection '{settings.qdrant_collection}' with 768-dim COSINE vectors.")


if __name__ == "__main__":
    main()
