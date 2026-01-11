"""
Pydantic модели для валидации ответов от Spring Boot API.
"""
from pydantic import BaseModel, Field
from typing import Optional


class SuccessResponse(BaseModel):
    """Модель успешного ответа."""
    result: str = Field(default="OK", pattern="^OK$")


class ErrorResponse(BaseModel):
    """Модель ответа с ошибкой."""
    result: str = Field(default="ERROR", pattern="^ERROR$")
    message: str
