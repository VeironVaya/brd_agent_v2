from tests.conftest import create_conversation, register_and_login


async def test_owner_shares_conversation_and_collaborator_sees_it(client):
    owner = await register_and_login(client, name="Owner")
    collaborator = await register_and_login(client, name="Collaborator")
    conv_id = await create_conversation(client, owner["headers"], title="Shared BRD")

    res = await client.post(
        f"/api/conversations/{conv_id}/collaborators",
        json={"email": collaborator["email"], "role": "editor"},
        headers=owner["headers"],
    )
    assert res.status_code == 201, res.text
    body = res.json()
    assert body["role"] == "editor"
    assert body["email"] == collaborator["email"]

    list_res = await client.get("/api/conversations", headers=collaborator["headers"])
    items = list_res.json()["conversations"]
    shared = next(c for c in items if c["id"] == conv_id)
    assert shared["role"] == "editor"
    assert shared["owner_name"] == "Owner"

    owned_res = await client.get("/api/conversations", headers=owner["headers"])
    own_item = next(c for c in owned_res.json()["conversations"] if c["id"] == conv_id)
    assert own_item["role"] == "owner"
    assert own_item["owner_name"] is None


async def test_editor_can_chat_and_add_custom_sections_viewer_cannot(client):
    owner = await register_and_login(client, name="Owner")
    editor = await register_and_login(client, name="Editor")
    viewer = await register_and_login(client, name="Viewer")
    conv_id = await create_conversation(client, owner["headers"])

    for user, role in [(editor, "editor"), (viewer, "viewer")]:
        res = await client.post(
            f"/api/conversations/{conv_id}/collaborators",
            json={"email": user["email"], "role": role},
            headers=owner["headers"],
        )
        assert res.status_code == 201, res.text

    editor_msg = await client.post(
        f"/api/conversations/{conv_id}/rooms/general/messages",
        json={"text": "hi from editor"},
        headers=editor["headers"],
    )
    assert editor_msg.status_code == 200

    editor_section = await client.post(
        f"/api/conversations/{conv_id}/custom-sections",
        json={"target": None, "title": "Editor's section", "has_children": False},
        headers=editor["headers"],
    )
    assert editor_section.status_code == 201

    viewer_msg = await client.post(
        f"/api/conversations/{conv_id}/rooms/general/messages",
        json={"text": "hi from viewer"},
        headers=viewer["headers"],
    )
    assert viewer_msg.status_code == 403
    assert viewer_msg.json()["error"] == "forbidden"

    viewer_section = await client.post(
        f"/api/conversations/{conv_id}/custom-sections",
        json={"target": None, "title": "Viewer's section", "has_children": False},
        headers=viewer["headers"],
    )
    assert viewer_section.status_code == 403

    # Both editor and viewer can view detail and export — read + export
    # access is the one thing every collaborator role gets.
    for user in [editor, viewer]:
        detail_res = await client.get(f"/api/conversations/{conv_id}", headers=user["headers"])
        assert detail_res.status_code == 200

        generate_res = await client.post(
            f"/api/conversations/{conv_id}/generate", json={"format": "markdown"}, headers=user["headers"]
        )
        assert generate_res.status_code == 200


async def test_owner_updates_role_and_removes_collaborator(client):
    owner = await register_and_login(client, name="Owner")
    collaborator = await register_and_login(client, name="Collaborator")
    conv_id = await create_conversation(client, owner["headers"])

    add_res = await client.post(
        f"/api/conversations/{conv_id}/collaborators",
        json={"email": collaborator["email"], "role": "viewer"},
        headers=owner["headers"],
    )
    collaborator_id = add_res.json()["id"]

    denied = await client.post(
        f"/api/conversations/{conv_id}/rooms/general/messages",
        json={"text": "not yet allowed"},
        headers=collaborator["headers"],
    )
    assert denied.status_code == 403

    update_res = await client.patch(
        f"/api/conversations/{conv_id}/collaborators/{collaborator_id}",
        json={"role": "editor"},
        headers=owner["headers"],
    )
    assert update_res.status_code == 200
    assert update_res.json()["role"] == "editor"

    allowed = await client.post(
        f"/api/conversations/{conv_id}/rooms/general/messages",
        json={"text": "now allowed"},
        headers=collaborator["headers"],
    )
    assert allowed.status_code == 200

    remove_res = await client.delete(
        f"/api/conversations/{conv_id}/collaborators/{collaborator_id}", headers=owner["headers"]
    )
    assert remove_res.status_code == 204

    revoked = await client.get(f"/api/conversations/{conv_id}", headers=collaborator["headers"])
    assert revoked.status_code == 404


async def test_only_owner_can_manage_collaborators(client):
    owner = await register_and_login(client, name="Owner")
    editor = await register_and_login(client, name="Editor")
    outsider = await register_and_login(client, name="Outsider")
    conv_id = await create_conversation(client, owner["headers"])

    await client.post(
        f"/api/conversations/{conv_id}/collaborators",
        json={"email": editor["email"], "role": "editor"},
        headers=owner["headers"],
    )

    # A collaborator (not the owner) can't manage other collaborators.
    forbidden_add = await client.post(
        f"/api/conversations/{conv_id}/collaborators",
        json={"email": outsider["email"], "role": "viewer"},
        headers=editor["headers"],
    )
    assert forbidden_add.status_code == 404  # editor has no owner-level access to this sub-resource at all

    # A collaborator can't rename or delete the conversation either.
    rename_res = await client.patch(
        f"/api/conversations/{conv_id}", json={"title": "Hijacked"}, headers=editor["headers"]
    )
    assert rename_res.status_code == 404
    delete_res = await client.delete(f"/api/conversations/{conv_id}", headers=editor["headers"])
    assert delete_res.status_code == 404


async def test_share_edge_cases(client):
    owner = await register_and_login(client, name="Owner")
    collaborator = await register_and_login(client, name="Collaborator")
    conv_id = await create_conversation(client, owner["headers"])

    unknown_email = await client.post(
        f"/api/conversations/{conv_id}/collaborators",
        json={"email": "nobody@example.com", "role": "editor"},
        headers=owner["headers"],
    )
    assert unknown_email.status_code == 404
    assert unknown_email.json()["error"] == "not_found"

    self_share = await client.post(
        f"/api/conversations/{conv_id}/collaborators",
        json={"email": owner["email"], "role": "editor"},
        headers=owner["headers"],
    )
    assert self_share.status_code == 400
    assert self_share.json()["error"] == "cannot_share_with_self"

    first = await client.post(
        f"/api/conversations/{conv_id}/collaborators",
        json={"email": collaborator["email"], "role": "editor"},
        headers=owner["headers"],
    )
    assert first.status_code == 201

    duplicate = await client.post(
        f"/api/conversations/{conv_id}/collaborators",
        json={"email": collaborator["email"], "role": "viewer"},
        headers=owner["headers"],
    )
    assert duplicate.status_code == 400
    assert duplicate.json()["error"] == "already_shared"
