from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class MissingPersonRecord(BaseModel):
    id: str
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    city: Optional[str] = None
    description: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    photos: List[str] = Field(default_factory=list)
    date_reported: Optional[datetime] = None
    created_at: Optional[datetime] = None


class MissingPersonCreate(BaseModel):
    name: str
    age: Optional[int] = Field(default=None, ge=0)
    gender: Optional[str] = None
    city: str
    description: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    photos: List[str] = Field(default_factory=list)
    date_reported: Optional[datetime] = None


class SightingCreate(BaseModel):
    missing_person_id: Optional[str] = None
    location: str
    reporter_name: str
    description: Optional[str] = None
    sighting_date: Optional[datetime] = None
    photo: Optional[str] = None
    reporter_phone: Optional[str] = None
    reporter_email: Optional[EmailStr] = None


class FeedbackCreate(BaseModel):
    match_id: str
    missing_person_id: Optional[str] = None
    sighting_id: Optional[str] = None
    is_correct: bool
    comments: Optional[str] = None


class MatchDecision(BaseModel):
    confidence: float
    decision: str
    reasons: List[str] = Field(default_factory=list)
