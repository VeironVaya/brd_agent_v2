from fastapi import APIRouter

from app.controllers import review_controller
from app.dtos.review_dtos import RecomputeReviewResponse

router = APIRouter(prefix="/api/conversations", tags=["review"])

router.add_api_route(
    "/{conversation_id}/review/recompute",
    review_controller.recompute_review,
    methods=["POST"],
    response_model=RecomputeReviewResponse,
)
