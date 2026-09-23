from pydantic import BaseModel
from typing import List

from sqlalchemy import Column, Integer, String, Numeric

from app.db.database import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    make = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)
    price = Column(Numeric(12, 2), nullable=False)
    transmission = Column(String(50), nullable=False)
    fuel_type = Column(String(50), nullable=False)


class VehicleResponse(BaseModel):
    make: str
    model: str
    year: int
    price: float
    transmission: str
    fuel_type: str

    class Config:
        orm_mode = True


class Answer(BaseModel):
    question_id: int
    alternative_id: int


class UserAnswer(BaseModel):
    user_id: int
    answers: List[Answer]
