from .helpers import create_conversation, register_and_login


async def test_create_conversation_seeds_full_template(client):
    session = await register_and_login(client)
    conv_id = await create_conversation(client, session["headers"])

    detail = (await client.get(f"/api/conversations/{conv_id}", headers=session["headers"])).json()
    assert detail["answered_count"] == 0
    assert detail["answers"] == {}  # sparse — no leaf touched yet
    assert detail["custom_sections"] == []
    assert detail["flagged_items"] == []
    assert detail["messages"] == {"general": []}
    assert detail["focused_field_id"] is None
    assert detail["last_generated_at"] is None

    # Proves all 26 template leaves + General room actually got seeded —
    # posting to a leaf and to general both succeed, a bogus room 404s.
    for room in ["1.1.1", "3.3.5", "5.1", "general"]:
        res = await client.post(
            f"/api/conversations/{conv_id}/rooms/{room}/messages",
            json={"text": "hello"},
            headers=session["headers"],
        )
        assert res.status_code == 200, f"room {room} should exist: {res.text}"

    bogus = await client.post(
        f"/api/conversations/{conv_id}/rooms/9.9.9/messages",
        json={"text": "hello"},
        headers=session["headers"],
    )
    assert bogus.status_code == 404


async def test_create_conversation_requires_title(client):
    session = await register_and_login(client)
    res = await client.post("/api/conversations", json={"title": "   "}, headers=session["headers"])
    assert res.status_code == 400
    assert res.json()["error"] == "title_required"


async def test_list_conversations_shows_answered_count(client):
    session = await register_and_login(client)
    await create_conversation(client, session["headers"], title="First BRD")

    res = await client.get("/api/conversations", headers=session["headers"])
    assert res.status_code == 200
    items = res.json()["conversations"]
    assert any(c["title"] == "First BRD" and c["answered_count"] == 0 for c in items)


async def test_rename_conversation(client):
    session = await register_and_login(client)
    conv_id = await create_conversation(client, session["headers"])

    res = await client.patch(
        f"/api/conversations/{conv_id}", json={"title": "Renamed BRD"}, headers=session["headers"]
    )
    assert res.status_code == 200
    assert res.json()["title"] == "Renamed BRD"

    empty = await client.patch(
        f"/api/conversations/{conv_id}", json={"title": ""}, headers=session["headers"]
    )
    assert empty.status_code == 400


async def test_delete_conversation_cascades(client):
    session = await register_and_login(client)
    conv_id = await create_conversation(client, session["headers"])

    delete_res = await client.delete(f"/api/conversations/{conv_id}", headers=session["headers"])
    assert delete_res.status_code == 204

    get_res = await client.get(f"/api/conversations/{conv_id}", headers=session["headers"])
    assert get_res.status_code == 404


async def test_conversation_not_owned_by_caller_is_404_not_403(client):
    """Deliberately 404, not 403 — doesn't confirm the id exists to a non-owner."""
    owner = await register_and_login(client)
    conv_id = await create_conversation(client, owner["headers"])

    other = await register_and_login(client)

    get_res = await client.get(f"/api/conversations/{conv_id}", headers=other["headers"])
    assert get_res.status_code == 404

    rename_res = await client.patch(
        f"/api/conversations/{conv_id}", json={"title": "Hijacked"}, headers=other["headers"]
    )
    assert rename_res.status_code == 404

    delete_res = await client.delete(f"/api/conversations/{conv_id}", headers=other["headers"])
    assert delete_res.status_code == 404

    message_res = await client.post(
        f"/api/conversations/{conv_id}/rooms/general/messages",
        json={"text": "hi"},
        headers=other["headers"],
    )
    assert message_res.status_code == 404


async def test_unauthenticated_requests_are_401(client):
    res = await client.get("/api/conversations")
    assert res.status_code == 401
