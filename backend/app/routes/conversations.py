from fastapi import APIRouter, status

from app.controllers import conversation_controller
from app.dtos.conversation_dtos import (
    ConversationDetailResponse,
    ConversationListResponse,
    CreateConversationResponse,
    RenameConversationResponse,
)

router = APIRouter(prefix="/api/conversations", tags=["conversations"])

router.add_api_route("", conversation_controller.list_conversations, methods=["GET"], response_model=ConversationListResponse)
router.add_api_route("", conversation_controller.create_conversation, methods=["POST"], response_model=CreateConversationResponse, status_code=status.HTTP_201_CREATED)
router.add_api_route("/{conversation_id}", conversation_controller.get_conversation_detail, methods=["GET"], response_model=ConversationDetailResponse)
router.add_api_route("/{conversation_id}", conversation_controller.rename_conversation, methods=["PATCH"], response_model=RenameConversationResponse)
router.add_api_route("/{conversation_id}", conversation_controller.delete_conversation, methods=["DELETE"], status_code=status.HTTP_204_NO_CONTENT)
