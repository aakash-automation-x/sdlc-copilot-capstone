from pydantic import BaseModel
from typing import List, Optional


class Answer(BaseModel):
    question_id: int
    alternative_id: int


class UserAnswer(BaseModel):
    user_id: int
    answers: List[Answer]


class Vehicle(BaseModel):
    """Vehicle details schema - FR-001, AC-001"""
    id: int
    name: str
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    price: str
    transmission: Optional[str] = None
    fuel_type: str
    category: str
    link: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "name": "Volkswagen ID.3",
                "make": "Volkswagen",
                "model": "ID.3",
                "year": 2024,
                "price": "low",
                "transmission": "automatic",
                "fuel_type": "electric",
                "category": "compact",
                "link": ""
            }
        }