"""
Service Layer - Business Logic & HTTP Error Handling

This module implements the business logic layer for the Car Portal API.
It acts as a bridge between the router layer (app/main.py) and the data layer
(app/db/models.py), handling:

- Vehicle retrieval orchestration (calls data layer fetch_vehicle)
- HTTP error handling (converts None → HTTPException 404)
- Structured logging for retrieval attempts and errors
- Pydantic model return types for FastAPI serialization

Architecture:
  Router (FastAPI endpoint) 
    → Service (get_vehicle, read_user, etc.)
    → Data (fetch_vehicle, JSON I/O)

This implements FR-001: System shall retrieve vehicle details by ID.
Supports AC-001 (HTTP 200 + all attributes) and AC-002 (HTTP 404 handling).

See also: app/main.py (Router), app/db/models.py (Data)
"""

import json
import logging
from typing import List, Dict, Optional
from fastapi import HTTPException

from app.db.models import Vehicle, fetch_vehicle

logger = logging.getLogger(__name__)

def get_vehicle(vehicle_id: int) -> Vehicle:
    """Retrieve vehicle by ID, raise 404 if not found.
    
    Maps to FR-001 (System retrieves vehicle details by ID) and AC-002 (handles not found).
    
    Args:
        vehicle_id: Integer vehicle ID to retrieve
        
    Returns:
        Vehicle model instance with all required attributes (AC-001)
        
    Raises:
        HTTPException(404): If vehicle not found (AC-002)
    """
    logger.info(f"Retrieving vehicle with ID: {vehicle_id}")
    vehicle = fetch_vehicle(vehicle_id)
    if vehicle is None:
        logger.warning(f"Vehicle not found: {vehicle_id}")
        raise HTTPException(status_code=404, detail="Vehicle not found")
    logger.info(f"Vehicle retrieved successfully: {vehicle_id}")
    return vehicle

def read_user():
    with open('data/users.json') as stream:
        users = json.load(stream)

    return users


def read_questions(position: int):
    with open('data/questions.json') as stream:
        questions = json.load(stream)

    for question in questions:
        if question['position'] == position:
            return question


def read_alternatives(question_id: int):
    alternatives_question = []
    with open('data/alternatives.json') as stream:
        alternatives = json.load(stream)

    for alternative in alternatives:
        if alternative['question_id'] == question_id:
            alternatives_question.append(alternative)

    return alternatives_question


def create_answer(payload):
    answers = []
    result = []

    with open('data/alternatives.json') as stream:
        alternatives = json.load(stream)

    for question in payload['answers']:
        for alternative in alternatives:
            if alternative['question_id'] == question['question_id']:
                answers.append(alternative['alternative'])
                break

    with open('data/cars.json') as stream:
        cars = json.load(stream)
        
    for car in cars:
        if answers[0] in car.values() and answers[1] in car.values() and answers[2] in car.values():
            result.append(car)

    return result


def read_result(user_id: int):
    user_result = []

    with open('data/results.json') as stream:
        results = json.load(stream)

    with open('data/users.json') as stream:
        users = json.load(stream)

    with open('data/cars.json') as stream:
        cars = json.load(stream)

    for result in results:
        if result['user_id'] == user_id:
            for user in users:
                if user['id'] == result['user_id']:
                    user_result.append({'user': user})
                    break

        for car_id in result['cars']:
            for car in cars:
                if car_id == car['id']:
                    user_result.append(car)

    return user_result