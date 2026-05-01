from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class MissingPersonRecord(BaseModel):
    id: str
    name: str
    height_cm: Optional[float] = None
    physical_features: List[str] = Field(default_factory=list)
    last_known_city: str
    reporter_email: EmailStr
    image_paths: List[str] = Field(default_factory=list)
    created_at: datetime


class MissingPersonCreate(BaseModel):
    name: str
    height_cm: Optional[float] = None
    physical_features: List[str] = Field(default_factory=list)
    last_known_city: str
    reporter_email: EmailStr


class SightingCreate(BaseModel):
    observed_features: List[str] = Field(default_factory=list)
    current_city: str
    description: Optional[str] = ""


class FeedbackCreate(BaseModel):
    match_id: str
    accepted: bool
    comments: Optional[str] = None


class MatchDecision(BaseModel):
    confidence: float
    decision: str
    reasons: List[str] = Field(default_factory=list)
