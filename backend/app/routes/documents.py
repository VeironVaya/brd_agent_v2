from fastapi import APIRouter

from app.controllers import document_controller
from app.dtos.document_dtos import GenerateDocumentResponse

router = APIRouter(prefix="/api/conversations", tags=["documents"])

router.add_api_route(
    "/{conversation_id}/generate",
    document_controller.generate_document,
    methods=["POST"],
    response_model=GenerateDocumentResponse,
)
