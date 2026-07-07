import logging
import socket
from typing import Any
from urllib.parse import urlparse

from langchain_core.tools import tool
from qdrant_client import QdrantClient
from qdrant_client.models import ScoredPoint

from core.config import settings

logger = logging.getLogger(__name__)

_qdrant: QdrantClient | None = None


def _get_qdrant() -> QdrantClient:
    global _qdrant
    if _qdrant is None:
        kwargs: dict[str, Any] = {"url": settings.qdrant_url, "check_compatibility": False}
        if settings.qdrant_api_key:
            kwargs["api_key"] = settings.qdrant_api_key
        _qdrant = QdrantClient(**kwargs)
    return _qdrant


def _qdrant_is_available() -> bool:
    parsed = urlparse(settings.qdrant_url)
    host = parsed.hostname or "localhost"
    port = parsed.port or 6333
    try:
        with socket.create_connection((host, port), timeout=0.5):
            return True
    except OSError:
        return False


def _embed(text: str) -> list[float]:
    from services.embedding_service import get_embedding
    return get_embedding(text)


@tool
def rag_search(query: str, top_k: int = 5, score_threshold: float = 0.7) -> list[dict]:
    """Search the agriculture knowledge base for relevant information.

    Args:
        query: The search query text.
        top_k: Number of results to return.
        score_threshold: Minimum similarity score (0–1).

    Returns:
        List of dicts with keys: text, source, score, topic.
    """
    try:
        if not _qdrant_is_available():
            logger.debug("RAGTool: Qdrant unavailable at %s; skipping retrieval.", settings.qdrant_url)
            return []

        client = _get_qdrant()
        vector = _embed(query)

        if hasattr(client, "query_points"):
            query_response = client.query_points(
                collection_name=settings.qdrant_collection,
                query=vector,
                limit=top_k,
                score_threshold=score_threshold,
                with_payload=True,
            )
            results: list[ScoredPoint] = list(query_response.points)
        else:
            results = client.search(
                collection_name=settings.qdrant_collection,
                query_vector=vector,
                limit=top_k,
                score_threshold=score_threshold,
                with_payload=True,
            )

        output = []
        for hit in results:
            payload = hit.payload or {}
            output.append({
                "text": payload.get("text", ""),
                "source": payload.get("source", "unknown"),
                "topic": payload.get("topic", ""),
                "score": round(hit.score, 4),
            })

        logger.debug("RAGTool: query=%r hits=%d", query[:50], len(output))
        return output

    except Exception as exc:
        logger.debug("RAGTool: search skipped/failed: %s", exc)
        return []
