from tests.conftest import create_conversation, register_and_login


async def _get_detail(client, headers, conv_id):
    return (await client.get(f"/api/conversations/{conv_id}", headers=headers)).json()


async def test_add_standalone_custom_section(client):
    session = await register_and_login(client)
    conv_id = await create_conversation(client, session["headers"])

    res = await client.post(
        f"/api/conversations/{conv_id}/custom-sections",
        json={"target": None, "title": "Vendor Escalation Path", "has_children": False, "purpose": "Routing."},
        headers=session["headers"],
    )
    assert res.status_code == 201
    body = res.json()
    assert body["title"] == "Vendor Escalation Path"
    assert body["purpose"] == "Routing."
    assert body["has_children"] is False

    detail = await _get_detail(client, session["headers"], conv_id)
    assert len(detail["custom_sections"]) == 1
    assert detail["custom_sections"][0]["nest_under"] is None


async def test_add_custom_section_nested_under_template(client):
    session = await register_and_login(client)
    conv_id = await create_conversation(client, session["headers"])

    res = await client.post(
        f"/api/conversations/{conv_id}/custom-sections",
        json={"target": {"kind": "template", "id": "3.3"}, "title": "Vendor Escalation Path", "has_children": False},
        headers=session["headers"],
    )
    assert res.status_code == 201

    detail = await _get_detail(client, session["headers"], conv_id)
    assert detail["custom_sections"][0]["nest_under"] == "3.3"


async def test_add_custom_section_under_unknown_template_key_404s(client):
    session = await register_and_login(client)
    conv_id = await create_conversation(client, session["headers"])

    res = await client.post(
        f"/api/conversations/{conv_id}/custom-sections",
        json={"target": {"kind": "template", "id": "99.99"}, "title": "Nowhere", "has_children": False},
        headers=session["headers"],
    )
    assert res.status_code == 404


async def test_arbitrary_depth_nesting(client):
    session = await register_and_login(client)
    conv_id = await create_conversation(client, session["headers"])
    headers = session["headers"]

    group = (
        await client.post(
            f"/api/conversations/{conv_id}/custom-sections",
            json={"target": None, "title": "Regional Rollout Notes", "has_children": True},
            headers=headers,
        )
    ).json()

    child = (
        await client.post(
            f"/api/conversations/{conv_id}/custom-sections",
            json={"target": {"kind": "custom", "id": group["id"]}, "title": "EMEA", "has_children": True},
            headers=headers,
        )
    ).json()

    grandchild = await client.post(
        f"/api/conversations/{conv_id}/custom-sections",
        json={"target": {"kind": "custom", "id": child["id"]}, "title": "UK", "has_children": False},
        headers=headers,
    )
    assert grandchild.status_code == 201

    detail = await _get_detail(client, headers, conv_id)
    tree = detail["custom_sections"]
    assert tree[0]["title"] == "Regional Rollout Notes"
    assert tree[0]["children"][0]["title"] == "EMEA"
    assert tree[0]["children"][0]["children"][0]["title"] == "UK"


async def test_rename_custom_section(client):
    session = await register_and_login(client)
    conv_id = await create_conversation(client, session["headers"])

    created = (
        await client.post(
            f"/api/conversations/{conv_id}/custom-sections",
            json={"target": None, "title": "Old Name", "has_children": False},
            headers=session["headers"],
        )
    ).json()

    res = await client.patch(
        f"/api/conversations/{conv_id}/custom-sections/{created['id']}",
        json={"title": "New Name"},
        headers=session["headers"],
    )
    assert res.status_code == 200
    assert res.json()["title"] == "New Name"


async def test_delete_custom_section_cascades_to_children(client):
    session = await register_and_login(client)
    conv_id = await create_conversation(client, session["headers"])
    headers = session["headers"]

    group = (
        await client.post(
            f"/api/conversations/{conv_id}/custom-sections",
            json={"target": None, "title": "Group", "has_children": True},
            headers=headers,
        )
    ).json()
    await client.post(
        f"/api/conversations/{conv_id}/custom-sections",
        json={"target": {"kind": "custom", "id": group["id"]}, "title": "Child", "has_children": False},
        headers=headers,
    )

    delete_res = await client.delete(
        f"/api/conversations/{conv_id}/custom-sections/{group['id']}", headers=headers
    )
    assert delete_res.status_code == 204

    detail = await _get_detail(client, headers, conv_id)
    assert detail["custom_sections"] == []  # group AND its child both gone


async def test_add_custom_section_requires_title(client):
    session = await register_and_login(client)
    conv_id = await create_conversation(client, session["headers"])

    res = await client.post(
        f"/api/conversations/{conv_id}/custom-sections",
        json={"target": None, "title": "  ", "has_children": False},
        headers=session["headers"],
    )
    assert res.status_code == 400
    assert res.json()["error"] == "title_required"
