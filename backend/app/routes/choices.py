from fastapi import APIRouter

from app.controllers import choice_controller
from app.dtos.choice_dtos import SaveChoicesResponse

router = APIRouter(prefix="/api/conversations", tags=["choices"])

router.add_api_route(
    "/{conversation_id}/sections/{section_id}/choices",
    choice_controller.save_choices,
    methods=["PUT"],
    response_model=SaveChoicesResponse,
)