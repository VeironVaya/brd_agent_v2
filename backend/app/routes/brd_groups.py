from fastapi import APIRouter, status

from app.controllers import brd_group_controller
from app.dtos.brd_group_dtos import (
    GroupCollaboratorDto,
    GroupCollaboratorListResponse,
    GroupDto,
    GroupListResponse,
)

router = APIRouter(tags=["groups"])

# Group CRUD
router.add_api_route(
    "/api/groups",
    brd_group_controller.list_groups,
    methods=["GET"],
    response_model=GroupListResponse,
)
router.add_api_route(
    "/api/groups",
    brd_group_controller.create_group,
    methods=["POST"],
    response_model=GroupDto,
    status_code=status.HTTP_201_CREATED,
)
router.add_api_route(
    "/api/groups/{group_id}",
    brd_group_controller.update_group,
    methods=["PATCH"],
    response_model=GroupDto,
)
router.add_api_route(
    "/api/groups/{group_id}",
    brd_group_controller.delete_group,
    methods=["DELETE"],
    status_code=status.HTTP_204_NO_CONTENT,
)

# Assign a BRD to a group (or unassign with group_id=null)
router.add_api_route(
    "/api/conversations/{conversation_id}/group",
    brd_group_controller.assign_group,
    methods=["PATCH"],
    status_code=status.HTTP_204_NO_CONTENT,
)

# ── Group sharing ─────────────────────────────────────────────────────────────

router.add_api_route(
    "/api/groups/{group_id}/collaborators",
    brd_group_controller.list_group_collaborators,
    methods=["GET"],
    response_model=GroupCollaboratorListResponse,
)
router.add_api_route(
    "/api/groups/{group_id}/collaborators",
    brd_group_controller.add_group_collaborator,
    methods=["POST"],
    response_model=GroupCollaboratorDto,
    status_code=status.HTTP_201_CREATED,
)
router.add_api_route(
    "/api/groups/{group_id}/collaborators/{collaborator_id}",
    brd_group_controller.update_group_collaborator_role,
    methods=["PATCH"],
    response_model=GroupCollaboratorDto,
)
router.add_api_route(
    "/api/groups/{group_id}/collaborators/{collaborator_id}",
    brd_group_controller.remove_group_collaborator,
    methods=["DELETE"],
    status_code=status.HTTP_204_NO_CONTENT,
)
