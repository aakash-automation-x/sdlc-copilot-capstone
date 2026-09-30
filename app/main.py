from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import Response

from app.db.database import Base, engine, get_db
from app.db.models import UserAnswer, VehicleResponse
from app.api import api
from app.api.api import get_vehicle_by_id

app = FastAPI()

# DR-006: create all ORM-mapped tables on startup (idempotent; safe to call
# on every restart). app.db.models must be imported above so that the Vehicle
# class is defined and its table metadata is registered with Base before this
# call.
Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "Fast API in Python"}


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


@app.get("/vehicles/{vehicle_id}", response_model=VehicleResponse)
def read_vehicle_by_id(vehicle_id: int, db: Session = Depends(get_db)):
    """Retrieve vehicle details by ID - FR-001, AC-001."""
    vehicle = get_vehicle_by_id(vehicle_id, db)
    if vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle
