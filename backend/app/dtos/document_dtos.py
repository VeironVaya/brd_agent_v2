from typing import Literal

from pydantic import BaseModel


class GenerateDocumentRequest(BaseModel):
    format: Literal["pdf", "markdown", "docx"]


class GenerateDocumentResponse(BaseModel):
    filename: str
    markdown: str
