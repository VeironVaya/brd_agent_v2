from app.services.ai_integration import DUMMY_AI_REPLY
from tests.conftest import create_conversation, register_and_login


async def test_post_message_returns_user_and_dummy_agent_reply(client):
    session = await register_and_login(client)
    conv_id = await create_conversation(client, session["headers"])

    res = await client.post(
        f"/api/conversations/{conv_id}/rooms/3.2/messages",
        json={"text": "Vendor master data lives in SAP Ariba."},
        headers=session["headers"],
    )
    assert res.status_code == 200
    messages = res.json()["messages"]
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[0]["text"] == "Vendor master data lives in SAP Ariba."
    assert messages[1]["role"] == "agent"
    assert messages[1]["text"] == DUMMY_AI_REPLY  # proves the stub is what's wired, not a real model


async def test_message_in_template_room_sets_focused_field(client):
    session = await register_and_login(client)
    conv_id = await create_conversation(client, session["headers"])

    detail_before = (await client.get(f"/api/conversations/{conv_id}", headers=session["headers"])).json()
    assert detail_before["focused_field_id"] is None

    await client.post(
        f"/api/conversations/{conv_id}/rooms/3.2/messages",
        json={"text": "hello"},
        headers=session["headers"],
    )

    detail_after = (await client.get(f"/api/conversations/{conv_id}", headers=session["headers"])).json()
    assert detail_after["focused_field_id"] == "3.2"
    assert "3.2" in detail_after["messages"]
    assert len(detail_after["messages"]["3.2"]) == 2


async def test_message_in_general_room_does_not_change_focus(client):
    session = await register_and_login(client)
    conv_id = await create_conversation(client, session["headers"])

    await client.post(
        f"/api/conversations/{conv_id}/rooms/3.2/messages",
        json={"text": "hello"},
        headers=session["headers"],
    )
    await client.post(
        f"/api/conversations/{conv_id}/rooms/general/messages",
        json={"text": "unrelated question"},
        headers=session["headers"],
    )

    detail = (await client.get(f"/api/conversations/{conv_id}", headers=session["headers"])).json()
    assert detail["focused_field_id"] == "3.2"  # still 3.2, general shouldn't have stolen focus
    assert len(detail["messages"]["general"]) == 2


async def test_post_message_to_nonexistent_room_404s(client):
    session = await register_and_login(client)
    conv_id = await create_conversation(client, session["headers"])

    res = await client.post(
        f"/api/conversations/{conv_id}/rooms/not-a-real-room/messages",
        json={"text": "hello"},
        headers=session["headers"],
    )
    assert res.status_code == 404


async def test_message_in_leaf_room_updates_the_answer(client):
    """The real pipeline the dummy AI now drives end to end: a message
    to a leaf room should actually create/update that leaf's Answer —
    this used to be an explicit no-op (see chat_service.py's history)."""
    session = await register_and_login(client)
    conv_id = await create_conversation(client, session["headers"])

    before = (await client.get(f"/api/conversations/{conv_id}", headers=session["headers"])).json()
    assert "3.2" not in before["answers"]  # nothing recorded yet

    await client.post(
        f"/api/conversations/{conv_id}/rooms/3.2/messages",
        json={"text": "Vendor master data lives in SAP Ariba."},
        headers=session["headers"],
    )

    after = (await client.get(f"/api/conversations/{conv_id}", headers=session["headers"])).json()
    answer = after["answers"]["3.2"]
    assert answer["status"] == "progress"
    assert answer["completeness"] > 0
    assert answer["confidence"] is not None
    assert "Vendor master data lives in SAP Ariba." in answer["answer"]
    assert answer["missing"]  # not complete yet, should still have a gap listed


async def test_leaf_answer_reaches_done_after_enough_turns(client):
    session = await register_and_login(client)
    conv_id = await create_conversation(client, session["headers"])

    for i in range(3):
        res = await client.post(
            f"/api/conversations/{conv_id}/rooms/3.2/messages",
            json={"text": f"Turn {i}"},
            headers=session["headers"],
        )
        assert res.status_code == 200

    detail = (await client.get(f"/api/conversations/{conv_id}", headers=session["headers"])).json()
    answer = detail["answers"]["3.2"]
    assert answer["completeness"] == 100
    assert answer["status"] == "done"
    assert answer["missing"] == []
    assert detail["answered_count"] == 1


async def test_message_in_general_room_never_creates_an_answer(client):
    session = await register_and_login(client)
    conv_id = await create_conversation(client, session["headers"])

    await client.post(
        f"/api/conversations/{conv_id}/rooms/general/messages",
        json={"text": "unrelated question"},
        headers=session["headers"],
    )

    detail = (await client.get(f"/api/conversations/{conv_id}", headers=session["headers"])).json()
    assert detail["answers"] == {}  # General is never a leaf — no Answer row, ever
