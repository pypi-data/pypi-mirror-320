"""Base response models."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    """Base response model."""

    success: bool = Field(..., description="Whether the request was successful")
    message: Optional[str] = Field(None, description="Response message")
    code: Optional[str] = Field(None, description="Response code")


class SuccessResponse(BaseResponse):
    """Success response model."""

    success: bool = Field(True, description="Request was successful")
    data: Optional[Any] = Field(None, description="Response data")
    meta: Optional[Dict[str, Any]] = Field(None, description="Response metadata")


class ErrorResponse(BaseResponse):
    """Error response model."""

    success: bool = Field(False, description="Request failed")
    error: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")
    errors: Optional[List[Dict[str, Any]]] = Field(None, description="List of errors")


class PaginatedResponse(SuccessResponse):
    """Paginated response model."""

    data: List[Any] = Field(..., description="List of items")
    meta: Dict[str, Any] = Field(
        ...,
        description="Pagination metadata",
        example={"page": 1, "per_page": 10, "total": 100, "total_pages": 10},
    )
