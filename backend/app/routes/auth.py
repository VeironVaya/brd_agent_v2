from fastapi import APIRouter, status

from app.controllers import auth_controller
from app.dtos.auth_dtos import AuthResponse, SessionResponse

router = APIRouter(prefix="/auth", tags=["auth"])

router.add_api_route("/register", auth_controller.register, methods=["POST"], response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
router.add_api_route("/login", auth_controller.login, methods=["POST"], response_model=AuthResponse)
router.add_api_route("/session", auth_controller.get_session, methods=["GET"], response_model=SessionResponse)
router.add_api_route("/logout", auth_controller.logout, methods=["POST"], status_code=status.HTTP_204_NO_CONTENT)
