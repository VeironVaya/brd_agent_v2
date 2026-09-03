import uuid
from httpx import AsyncClient


async def register_and_login(client: AsyncClient, *, name: str = "Test User") -> dict:
    """Registers a fresh unique user and returns {"headers", "user", "email"}."""
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
