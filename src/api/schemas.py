from __future__ import annotations

from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    area: float = Field(..., gt=0)
    perimeter: float = Field(..., gt=0)
    compactness: float = Field(..., gt=0)
    kernel_length: float = Field(..., gt=0)
    kernel_width: float = Field(..., gt=0)
    asymmetry_coefficient: float = Field(..., ge=0)
    groove_length: float = Field(..., gt=0)


class PredictResponse(BaseModel):
    predicted_class: int
    class_name: str
