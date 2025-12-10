from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    base64_image: str = Field(..., description="Image encoded as data URL or plain base64 string")


class AnalyzeResponse(BaseModel):
    design_score: int = Field(0, ge=0, le=10)
    material_quality_focus: float = Field(0.0, ge=0.0, le=10.0)
    lifestyle_context_score: float = Field(0.0, ge=0.0, le=10.0)
    summary: str = ""

