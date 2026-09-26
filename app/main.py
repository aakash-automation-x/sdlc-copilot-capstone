from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.responses import Response, FileResponse

from app.db.database import engine, get_db
from app.db import models
from app.db.models import UserAnswer, VehicleResponse
from app.api import api

SEED_VEHICLES = [
    {"make": "Volkswagen", "model": "ID.3",    "year": 2024, "price": 35000.00, "transmission": "Automatic", "fuel_type": "Electric"},
    {"make": "Porsche",    "model": "Taycan",  "year": 2024, "price": 95000.00, "transmission": "Automatic", "fuel_type": "Electric"},
    {"make": "Tesla",      "model": "Model 3", "year": 2023, "price": 42000.00, "transmission": "Automatic", "fuel_type": "Electric"},
    {"make": "Vauxhall",   "model": "e-Corsa", "year": 2023, "price": 30000.00, "transmission": "Automatic", "fuel_type": "Electric"},
    {"make": "Mini",       "model": "Electric","year": 2024, "price": 38000.00, "transmission": "Automatic", "fuel_type": "Electric"},
    {"make": "Chevrolet",  "model": "Onix",    "year": 2023, "price": 18000.00, "transmission": "Manual",    "fuel_type": "Biofuel"},
    {"make": "Ford",       "model": "Ka",      "year": 2022, "price": 15000.00, "transmission": "Manual",    "fuel_type": "Biofuel"},
    {"make": "Hyundai",    "model": "Creta",   "year": 2024, "price": 27000.00, "transmission": "Automatic", "fuel_type": "Petrol"},
    {"make": "Chery",      "model": "Tiggo 2", "year": 2023, "price": 20000.00, "transmission": "Automatic", "fuel_type": "Biofuel"},
    {"make": "Chevrolet",  "model": "Opala",   "year": 2022, "price": 60000.00, "transmission": "Manual",    "fuel_type": "Petrol"},
]


def _seed_db():
    models.Base.metadata.create_all(bind=engine)
    db = next(get_db())
    try:
        if db.query(models.Vehicle).count() == 0:
            db.bulk_insert_mappings(models.Vehicle, SEED_VEHICLES)
            db.commit()
    finally:
        db.close()


app = FastAPI(on_startup=[_seed_db])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


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
    payload = payload.model_dump()

    return api.create_answer(payload)


@app.get("/result/{user_id}")
def read_result(user_id: int):
    return api.read_result(user_id)


@app.get("/vehicles/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    vehicle = api.get_vehicle_by_id(vehicle_id, db)
    if vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle


@app.get("/ui")
def get_ui():
    return FileResponse("static/index.html")
