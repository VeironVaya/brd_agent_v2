from fastapi import APIRouter

from app.controllers import chat_controller
from app.dtos.chat_dtos import PostMessageResponse

router = APIRouter(prefix="/api/conversations", tags=["chat"])

router.add_api_route(
    "/{conversation_id}/rooms/{room_id}/messages",
    chat_controller.post_message,
    methods=["POST"],
    response_model=PostMessageResponse,
)
