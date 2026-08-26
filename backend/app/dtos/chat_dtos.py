from pydantic import BaseModel, Field, field_validator

# Arbitrary but generous cap — prevents accidental or malicious payloads
# from inflating the LLM prompt unboundedly. 4 000 chars ≈ ~1 000 tokens,
# well within model context limits while still covering any realistic
# single message a user would actually type.
MAX_MESSAGE_LENGTH = 4000


class PostMessageRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=MAX_MESSAGE_LENGTH)

    @field_validator("text")
    @classmethod
    def text_not_blank(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Message cannot be blank.")
        return stripped


class MessageDto(BaseModel):
    id: str
    role: str
    text: str


class PostMessageResponse(BaseModel):
    messages: list[MessageDto]

