"""
Integration tests for the auth flow.
Requires: MongoDB running (set TEST_MONGO_URI env var or use mongomock).
Run with: pytest tests/integration/ -v --asyncio-mode=auto
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport


@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture(scope="module")
async def client():
    """Start the FastAPI app with a test MongoDB database."""
    import os
    os.environ.setdefault("MONGO_URI", "mongodb://localhost:27017")
    os.environ.setdefault("MONGO_DB_NAME", "krishi_test")
    os.environ.setdefault("APP_SECRET_KEY", "test-secret-key-for-ci-only")
    os.environ.setdefault("REDIS_URL", "redis://localhost:6379/1")
    os.environ.setdefault("LLM_PROVIDER", "groq")
    os.environ.setdefault("GROQ_API_KEY", "test-key")

    from main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.mark.anyio
async def test_health(client: AsyncClient):
    res = await client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


@pytest.mark.anyio
async def test_register_and_login(client: AsyncClient):
    phone = "9876543210"

    # Register
    res = await client.post("/api/v1/auth/register", json={
        "phone": phone,
        "password": "testpass123",
        "full_name": "Test Farmer",
    })
    assert res.status_code in (201, 400)  # 400 if already exists from prior run

    # Login
    res = await client.post("/api/v1/auth/login", json={
        "phone": phone,
        "password": "testpass123",
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert "refresh_token" in data
    return data


@pytest.mark.anyio
async def test_me_endpoint_requires_auth(client: AsyncClient):
    res = await client.get("/api/v1/auth/me")
    assert res.status_code == 401


@pytest.mark.anyio
async def test_me_endpoint_with_token(client: AsyncClient):
    # Login first
    login_res = await client.post("/api/v1/auth/login", json={
        "phone": "9876543210",
        "password": "testpass123",
    })
    if login_res.status_code != 200:
        pytest.skip("Login failed — run test_register_and_login first")

    token = login_res.json()["access_token"]
    res = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["phone"] == "9876543210"


@pytest.mark.anyio
async def test_invalid_credentials(client: AsyncClient):
    res = await client.post("/api/v1/auth/login", json={
        "phone": "0000000000",
        "password": "wrongpassword",
    })
    assert res.status_code == 401
