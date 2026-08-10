from fastapi import APIRouter, status

from app.controllers import custom_section_controller
from app.dtos.custom_section_dtos import AddCustomSectionResponse, RenameCustomSectionResponse

router = APIRouter(prefix="/api/conversations", tags=["custom-sections"])

router.add_api_route(
    "/{conversation_id}/custom-sections",
    custom_section_controller.add_custom_section,
    methods=["POST"],
    response_model=AddCustomSectionResponse,
    status_code=status.HTTP_201_CREATED,
)
router.add_api_route(
    "/{conversation_id}/custom-sections/{section_id}",
    custom_section_controller.rename_custom_section,
    methods=["PATCH"],
    response_model=RenameCustomSectionResponse,
)
router.add_api_route(
    "/{conversation_id}/custom-sections/{section_id}",
    custom_section_controller.remove_custom_section,
    methods=["DELETE"],
    status_code=status.HTTP_204_NO_CONTENT,
)
