from fastapi import APIRouter, status

from app.controllers import share_controller
from app.dtos.share_dtos import CollaboratorDto, CollaboratorListResponse

router = APIRouter(prefix="/api/conversations", tags=["sharing"])

router.add_api_route(
    "/{conversation_id}/collaborators",
    share_controller.add_collaborator,
    methods=["POST"],
    response_model=CollaboratorDto,
    status_code=status.HTTP_201_CREATED,
)
router.add_api_route(
    "/{conversation_id}/collaborators",
    share_controller.list_collaborators,
    methods=["GET"],
    response_model=CollaboratorListResponse,
)
router.add_api_route(
    "/{conversation_id}/collaborators/{collaborator_id}",
    share_controller.update_collaborator_role,
    methods=["PATCH"],
    response_model=CollaboratorDto,
)
router.add_api_route(
    "/{conversation_id}/collaborators/{collaborator_id}",
    share_controller.remove_collaborator,
    methods=["DELETE"],
    status_code=status.HTTP_204_NO_CONTENT,
)
