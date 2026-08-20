from tests.conftest import create_conversation, register_and_login


async def test_save_choice_section_updates_answer_and_returns_choices(client):
    session = await register_and_login(client)
    conversation_id = await create_conversation(client, session["headers"])

    response = await client.put(
        f"/api/conversations/{conversation_id}/sections/1.3/choices",
        json={
            "choice_data": {
                "selected": {
                    "selected": ["BR for new service/application/process", "Others, please specify"],
                    "other_text": "Modernization of the channel platform",
                },
            }
        },
        headers=session["headers"],
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "done"
    assert body["choice_data"]["selected"]["selected"] == [
        "BR for new service/application/process",
        "Others, please specify",
    ]
    assert "Modernization of the channel platform" in body["answer"]

    detail = (await client.get(f"/api/conversations/{conversation_id}", headers=session["headers"])).json()
    assert detail["answers"]["1.3"]["choice_data"] == body["choice_data"]


async def test_save_choice_section_rejects_missing_other_text(client):
    session = await register_and_login(client)
    conversation_id = await create_conversation(client, session["headers"])

    response = await client.put(
        f"/api/conversations/{conversation_id}/sections/1.3/choices",
        json={"choice_data": {"selected": {"selected": ["Others, please specify"], "other_text": ""}}},
        headers=session["headers"],
    )

    assert response.status_code == 400
    assert response.json()["error"] == "invalid_choice_data"


async def test_save_product_specification_choices_requires_all_groups(client):
    session = await register_and_login(client)
    conversation_id = await create_conversation(client, session["headers"])

    response = await client.put(
        f"/api/conversations/{conversation_id}/sections/3.2/choices",
        json={"choice_data": {"target_market_segmentation": {"selected": ["SME"], "other_text": ""}}},
        headers=session["headers"],
    )

    assert response.status_code == 400
    assert response.json()["error"] == "invalid_choice_data"


async def test_conversation_stores_first_page_metadata(client):
    session = await register_and_login(client)
    response = await client.post(
        "/api/conversations",
        json={
            "title": "Modern Channel Hub",
            "requestor_directorate": "Sales",
            "impacted_stakeholders": ["Sales", "Planning & Transformation (P&T)"],
        },
        headers=session["headers"],
    )
    conversation_id = response.json()["id"]

    detail = (await client.get(f"/api/conversations/{conversation_id}", headers=session["headers"])).json()
    assert detail["requestor_directorate"] == "Sales"
    assert detail["impacted_stakeholders"] == ["Sales", "Planning & Transformation (P&T)"]