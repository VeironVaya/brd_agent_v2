from pydantic import BaseModel


class PostMessageRequest(BaseModel):
    text: str


class MessageDto(BaseModel):
    id: str
    role: str
    text: str


class PostMessageResponse(BaseModel):
    messages: list[MessageDto]
