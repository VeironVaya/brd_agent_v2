from fastapi import APIRouter

from app.routes import auth, chat, conversations, custom_sections, documents, review

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(conversations.router)
api_router.include_router(chat.router)
api_router.include_router(custom_sections.router)
api_router.include_router(review.router)
api_router.include_router(documents.router)
