import uuid

from tests.conftest import register_and_login


async def test_register_returns_user_and_token(client):
    email = f"{uuid.uuid4()}@example.com"
    res = await client.post(
        "/auth/register", json={"email": email, "password": "password123", "name": "Alice"}
    )
    assert res.status_code == 201
    body = res.json()
    assert body["user"]["email"] == email
    assert body["user"]["name"] == "Alice"
    assert "password" not in body["user"]
    assert "password_hash" not in body["user"]
    assert body["token"]


async def test_register_duplicate_email_is_rejected(client):
    email = f"{uuid.uuid4()}@example.com"
    first = await client.post(
        "/auth/register", json={"email": email, "password": "password123", "name": "Alice"}
    )
    assert first.status_code == 201

    second = await client.post(
        "/auth/register", json={"email": email, "password": "password123", "name": "Alice Again"}
    )
    assert second.status_code == 400
    assert second.json()["error"] == "email_taken"


async def test_register_rejects_short_password(client):
    email = f"{uuid.uuid4()}@example.com"
    res = await client.post("/auth/register", json={"email": email, "password": "short", "name": "Alice"})
    assert res.status_code == 400
    assert res.json()["error"] == "invalid_registration"


async def test_login_success(client):
    session = await register_and_login(client)
    res = await client.post("/auth/login", json={"email": session["email"], "password": "password123"})
    assert res.status_code == 200
    assert res.json()["user"]["email"] == session["email"]


async def test_login_wrong_password(client):
    session = await register_and_login(client)
    res = await client.post("/auth/login", json={"email": session["email"], "password": "wrong-password"})
    assert res.status_code == 401
    assert res.json()["error"] == "invalid_credentials"


async def test_login_nonexistent_email_same_error_as_wrong_password(client):
    """api_contract.md §1: same error either way, so an attacker can't enumerate registered emails."""
    res = await client.post(
        "/auth/login", json={"email": f"{uuid.uuid4()}@example.com", "password": "whatever123"}
    )
    assert res.status_code == 401
    assert res.json()["error"] == "invalid_credentials"


async def test_session_requires_valid_token(client):
    session = await register_and_login(client)

    ok = await client.get("/auth/session", headers=session["headers"])
    assert ok.status_code == 200
    assert ok.json()["user"]["email"] == session["email"]

    missing = await client.get("/auth/session")
    assert missing.status_code == 401

    garbage = await client.get("/auth/session", headers={"Authorization": "Bearer not-a-real-token"})
    assert garbage.status_code == 401


async def test_logout_returns_no_content(client):
    session = await register_and_login(client)
    res = await client.post("/auth/logout", headers=session["headers"])
    assert res.status_code == 204
