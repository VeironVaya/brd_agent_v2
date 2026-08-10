"""Test setup: a dedicated brdagent_test database (created/migrated fresh
each session), an httpx client against the real FastAPI app, and helpers
that dogfood the real /auth endpoints to get authenticated headers rather
than reaching into the DB directly — these are black-box integration
tests against the actual API surface, matching implementation_1.md's
"controllers get thin request/response contract tests" plus enough
service-level behavior coverage (seeding, nesting, flagged detection) to
count as real regression coverage, not just status-code checks.
"""

import os
import uuid

os.environ["DATABASE_URL"] = "postgresql+asyncpg://brdagent:brdagent@127.0.0.1:5432/brdagent_test"
os.environ.setdefault("JWT_SECRET", "test-secret-at-least-32-bytes-long-for-hs256")

import asyncpg
import pytest
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADMIN_DATABASE_URL = "postgresql://brdagent:brdagent@127.0.0.1:5432/postgres"
TEST_DB_NAME = "brdagent_test"


@pytest.fixture(scope="session", autouse=True)
def _setup_test_database():
    import asyncio

    async def _recreate():
        conn = await asyncpg.connect(ADMIN_DATABASE_URL)
        try:
            await conn.execute(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}" WITH (FORCE)')
            await conn.execute(f'CREATE DATABASE "{TEST_DB_NAME}"')
        finally:
            await conn.close()

    asyncio.run(_recreate())

    cfg = Config(os.path.join(BACKEND_DIR, "alembic.ini"))
    cfg.set_main_option("script_location", os.path.join(BACKEND_DIR, "migrations"))
    cfg.set_main_option(
        "sqlalchemy.url", "postgresql+asyncpg://brdagent:brdagent@127.0.0.1:5432/brdagent_test"
    )
    command.upgrade(cfg, "head")


@pytest.fixture
async def client():
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def register_and_login(client: AsyncClient, *, name: str = "Test User") -> dict:
    """Registers a fresh unique user and returns {"headers", "user"}."""
    email = f"{uuid.uuid4()}@example.com"
    res = await client.post(
        "/auth/register", json={"email": email, "password": "password123", "name": name}
    )
    assert res.status_code == 201, res.text
    body = res.json()
    return {"headers": {"Authorization": f"Bearer {body['token']}"}, "user": body["user"], "email": email}


async def create_conversation(client: AsyncClient, headers: dict, title: str = "Test BRD") -> str:
    res = await client.post("/api/conversations", json={"title": title}, headers=headers)
    assert res.status_code == 201, res.text
    return res.json()["id"]
