from typing import List

from sqlalchemy import Column, Integer, String
from pydantic import BaseModel, ConfigDict

from app.db.database import Base  # FR-001, DR-004


class Answer(BaseModel):
    question_id: int
    alternative_id: int


class UserAnswer(BaseModel):
    user_id: int
    answers: List[Answer]


class Vehicle(Base):
    """SQLAlchemy ORM model for the vehicles table - FR-001, DR-003."""

    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, nullable=False)
    make = Column(String, nullable=False)
    model = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    price = Column(String, nullable=False)
    transmission = Column(String, nullable=False)
    fuel_type = Column(String, nullable=False)


class VehicleResponse(BaseModel):
    """Pydantic v2 response schema for the Vehicle ORM model - FR-001, DR-002."""

    id: int
    make: str
    model: str
    year: int
    price: str
    transmission: str
    fuel_type: str

    model_config = ConfigDict(from_attributes=True)
