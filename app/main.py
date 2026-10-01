from fastapi import FastAPI, HTTPException, Path
from starlette.responses import Response

from app.db.models import UserAnswer
from app.api import api

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Fast API in Python"}


@app.get("/vehicles/{vehicle_id}", status_code=200)
def read_vehicle(vehicle_id: int = Path(..., gt=0, description="Vehicle ID must be greater than 0")):
    """Get vehicle details by ID.
    
    Maps to FR-001: System retrieves vehicle details by ID.
    Supports AC-001 (returns vehicle with all attributes) and AC-002 (404 when not found).
    
    Args:
        vehicle_id (int): Vehicle ID (must be > 0, validated by FastAPI)
        
    Returns:
        Vehicle model with id, make, model, year, price, transmission, fuel_type (AC-001)
        
    Raises:
        HTTPException(422): If vehicle_id <= 0 (FastAPI validation)
        HTTPException(404): If vehicle not found (AC-002)
    """
    return api.get_vehicle(vehicle_id)


@app.get("/user")
def read_user():
    return api.read_user()


@app.get("/question/{position}", status_code=200)
def read_questions(position: int, response: Response):
    question = api.read_questions(position)

    if not question:
        raise HTTPException(status_code=400, detail="Error")

    return question


@app.get("/alternatives/{question_id}")
def read_alternatives(question_id: int):
    return api.read_alternatives(question_id)


@app.post("/answer", status_code=201)
def create_answer(payload: UserAnswer):
    payload = payload.dict()

    return api.create_answer(payload)


@app.get("/result/{user_id}")
def read_result(user_id: int):
    return api.read_result(user_id)
