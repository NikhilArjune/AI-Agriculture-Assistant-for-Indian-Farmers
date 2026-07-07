import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def mock_farmer_profile() -> dict:
    return {
        "user_id": "64f1a2b3c4d5e6f7a8b9c0d1",
        "full_name": "Ramesh Kumar",
        "preferred_lang": "hi",
        "location": {
            "state": "Punjab",
            "district": "Ludhiana",
            "village": "Khanna",
            "coordinates": {"lat": 30.9, "lng": 75.8},
        },
        "farm_size_acres": 5.0,
        "soil_type": "loamy",
        "irrigation_type": "drip",
        "primary_crops": ["wheat", "rice"],
    }


@pytest.fixture
def mock_agri_state(mock_farmer_profile) -> dict:
    return {
        "user_id": "64f1a2b3c4d5e6f7a8b9c0d1",
        "session_id": "test-session-001",
        "query": "What is the best time to sow wheat in Punjab?",
        "language": "en",
        "intent": "",
        "active_agent": "",
        "image_base64": None,
        "farmer_profile": mock_farmer_profile,
        "retrieved_context": [],
        "tool_outputs": {},
        "agent_response": "",
        "confidence": 0.0,
        "requires_human_help": False,
        "sources": [],
        "messages": [],
    }
