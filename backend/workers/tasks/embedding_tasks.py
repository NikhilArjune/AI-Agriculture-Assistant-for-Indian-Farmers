import logging

from workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def ingest_document(self, file_path: str, topic: str, source: str):
    """Parse a PDF/document and upsert its chunks into Qdrant."""
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(file_path)
        chunks = []
        for page in doc:
            text = page.get_text().strip()
            if len(text) > 100:
                # Split into ~500-char chunks with 50-char overlap
                for i in range(0, len(text), 450):
                    chunk = text[i : i + 500]
                    if chunk.strip():
                        chunks.append(chunk)
        doc.close()

        from services.embedding_service import get_embeddings_batch
        from qdrant_client import QdrantClient
        from qdrant_client.models import PointStruct
        from core.config import settings
        import uuid

        embeddings = get_embeddings_batch(chunks)
        client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)

        points = [
            PointStruct(
                id=str(uuid.uuid4()),
                vector=emb,
                payload={"text": chunk, "source": source, "topic": topic},
            )
            for chunk, emb in zip(chunks, embeddings)
        ]

        client.upsert(collection_name=settings.qdrant_collection, points=points)
        logger.info("Ingested %d chunks from %s into Qdrant", len(points), file_path)
        return {"status": "ok", "chunks_ingested": len(points)}

    except Exception as exc:
        logger.error("ingest_document failed: %s", exc)
        raise self.retry(exc=exc)


@celery_app.task
def refresh_market_embeddings():
    """Daily task: re-embed latest market price summaries into Qdrant."""
    logger.info("refresh_market_embeddings: starting daily refresh")
    # Placeholder — implement when market data pipeline is ready
    return {"status": "skipped", "reason": "not implemented"}
