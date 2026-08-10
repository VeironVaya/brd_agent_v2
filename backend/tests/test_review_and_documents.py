from datetime import datetime, timedelta, timezone

from app.db import SessionLocal
from app.repositories import answer_repository, section_repository
from app.services import review_service
from tests.conftest import create_conversation, register_and_login


async def test_recompute_review_empty_for_fresh_conversation(client):
    session = await register_and_login(client)
    conv_id = await create_conversation(client, session["headers"])

    res = await client.post(f"/api/conversations/{conv_id}/review/recompute", headers=session["headers"])
    assert res.status_code == 200
    assert res.json()["flagged_items"] == []


async def test_flagged_detection_when_prerequisite_answered_more_recently(client):
    """Exercises erd.md's actual worked query — 4.1 depends on 3.3.5 and 3.8.
    Posting real chat messages *can* now drive a leaf to 'done' through the
    API (see test_chat.py's test_leaf_answer_reaches_done_after_enough_turns)
    — but this test needs two answers hours apart with exact, controlled
    `answered_at` values to deterministically prove the ordering comparison,
    and every message-driven update stamps 'now()' at request time. No
    amount of API calls gets you that precision, so this goes straight at
    the service/repository layer instead, same as any other test that needs
    to control time precisely would."""
    session = await register_and_login(client)
    conv_id = await create_conversation(client, session["headers"])

    async with SessionLocal() as db:
        sections = await section_repository.list_by_conversation(db, conv_id)
        by_template_key = {s.template_key: s for s in sections}
        dependent = by_template_key["4.1"]
        prereq_a = by_template_key["3.3.5"]
        prereq_b = by_template_key["3.8"]

        earlier = datetime.now(timezone.utc) - timedelta(hours=2)
        later = datetime.now(timezone.utc)

        # Dependent answered first (done)...
        await answer_repository.upsert(
            db, dependent.section_id, status="done", answer_text="Target: Q2 next year.", touch_answered_at=False
        )
        dependent_answer = await answer_repository.find_by_section_id(db, dependent.section_id)
        dependent_answer.answered_at = earlier

        for prereq in (prereq_a, prereq_b):
            await answer_repository.upsert(db, prereq.section_id, status="done", answer_text="...", touch_answered_at=False)
            a = await answer_repository.find_by_section_id(db, prereq.section_id)
            a.answered_at = earlier

        await db.commit()

        # ...then one prerequisite (3.3.5) gets updated *after* the dependent was answered.
        await answer_repository.upsert(db, prereq_a.section_id, status="done", answer_text="Updated plan.", touch_answered_at=False)
        prereq_a_answer = await answer_repository.find_by_section_id(db, prereq_a.section_id)
        prereq_a_answer.answered_at = later
        await db.commit()

        flagged = await review_service.recompute(db, conv_id)

    assert any(item["field_id"] == "4.1" for item in flagged)
    item = next(item for item in flagged if item["field_id"] == "4.1")
    assert "3.3.5" in item["depends_on_label"]
    assert item["reason"]  # non-empty, regenerated text per erd.md's decision

    # And the API surfaces it too, both via recompute and via the answers map's `flagged` bool.
    res = await client.post(f"/api/conversations/{conv_id}/review/recompute", headers=session["headers"])
    assert any(fi["field_id"] == "4.1" for fi in res.json()["flagged_items"])

    detail = (await client.get(f"/api/conversations/{conv_id}", headers=session["headers"])).json()
    assert detail["answers"]["4.1"]["flagged"] is True


async def test_generate_document_markdown(client):
    session = await register_and_login(client)
    conv_id = await create_conversation(client, session["headers"], title="Export Test BRD")

    res = await client.post(
        f"/api/conversations/{conv_id}/generate", json={"format": "markdown"}, headers=session["headers"]
    )
    assert res.status_code == 200
    body = res.json()
    assert body["filename"] == "Export Test BRD.md"
    assert "# Export Test BRD" in body["markdown"]
    assert "## 1. Introduction" in body["markdown"]
    assert "## Document Signoff" in body["markdown"]


async def test_generate_document_pdf_filename(client):
    session = await register_and_login(client)
    conv_id = await create_conversation(client, session["headers"], title="Export Test BRD")

    res = await client.post(
        f"/api/conversations/{conv_id}/generate", json={"format": "pdf"}, headers=session["headers"]
    )
    assert res.status_code == 200
    assert res.json()["filename"] == "Export Test BRD.pdf"


async def test_generate_sets_last_generated_metadata(client):
    session = await register_and_login(client)
    conv_id = await create_conversation(client, session["headers"])

    before = (await client.get(f"/api/conversations/{conv_id}", headers=session["headers"])).json()
    assert before["last_generated_at"] is None

    await client.post(
        f"/api/conversations/{conv_id}/generate", json={"format": "markdown"}, headers=session["headers"]
    )

    after = (await client.get(f"/api/conversations/{conv_id}", headers=session["headers"])).json()
    assert after["last_generated_at"] is not None
    assert after["last_generated_version"] == "Version 1.0"


async def test_generate_includes_custom_sections_with_computed_codes(client):
    session = await register_and_login(client)
    conv_id = await create_conversation(client, session["headers"])
    headers = session["headers"]

    await client.post(
        f"/api/conversations/{conv_id}/custom-sections",
        json={"target": None, "title": "Regional Rollout Notes", "has_children": False},
        headers=headers,
    )

    res = await client.post(
        f"/api/conversations/{conv_id}/generate", json={"format": "markdown"}, headers=headers
    )
    markdown = res.json()["markdown"]
    assert "## Custom Sections" in markdown
    assert "**6 Regional Rollout Notes**" in markdown  # continues after the 5 top-level template sections


async def test_generate_for_unowned_conversation_404s(client):
    owner = await register_and_login(client)
    conv_id = await create_conversation(client, owner["headers"])

    other = await register_and_login(client)
    res = await client.post(
        f"/api/conversations/{conv_id}/generate", json={"format": "markdown"}, headers=other["headers"]
    )
    assert res.status_code == 404
