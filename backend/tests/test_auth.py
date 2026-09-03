import uuid

from .helpers import register_and_login


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


async def test_logout_requires_a_token(client):
    res = await client.post("/auth/logout")
    assert res.status_code == 401


async def test_logout_actually_revokes_the_token(client):
    """The real bug this was built for: logging out used to be a no-op —
    the same token kept authenticating successfully afterward. Proves the
    token is dead the moment logout returns, not just eventually on its
    natural expiry."""
    session = await register_and_login(client)

    before = await client.get("/auth/session", headers=session["headers"])
    assert before.status_code == 200

    logout_res = await client.post("/auth/logout", headers=session["headers"])
    assert logout_res.status_code == 204

    after = await client.get("/auth/session", headers=session["headers"])
    assert after.status_code == 401

    conversations = await client.get("/api/conversations", headers=session["headers"])
    assert conversations.status_code == 401


async def test_logout_is_idempotent(client):
    session = await register_and_login(client)
    first = await client.post("/auth/logout", headers=session["headers"])
    assert first.status_code == 204
    # Same (now-revoked) token again — must not 500 on a duplicate-key insert.
    second = await client.post("/auth/logout", headers=session["headers"])
    assert second.status_code == 204


async def test_logout_does_not_revoke_other_sessions(client):
    """Logging out on one device/token shouldn't kill a second, separately
    issued token for the same user (e.g. logged in on two tabs)."""
    session = await register_and_login(client)
    second_login = await client.post(
        "/auth/login", json={"email": session["email"], "password": "password123"}
    )
    assert second_login.status_code == 200
    second_headers = {"Authorization": f"Bearer {second_login.json()['token']}"}

    await client.post("/auth/logout", headers=session["headers"])

    first_still_dead = await client.get("/auth/session", headers=session["headers"])
    assert first_still_dead.status_code == 401

    second_still_alive = await client.get("/auth/session", headers=second_headers)
    assert second_still_alive.status_code == 200
