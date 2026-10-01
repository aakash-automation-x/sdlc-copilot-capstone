"""
Data Layer - Pydantic Models & JSON Persistence

This module implements the data layer for the Car Portal API, providing:

- Pydantic models for request/response validation (Answer, UserAnswer, Vehicle)
- JSON file I/O operations (fetch_vehicle, implicit via api.py)
- Data schema definitions with field types and examples

Architecture:
  Router (FastAPI endpoint, app/main.py)
    → Service (business logic, app/api/api.py)
    → Data (JSON I/O & models, this module)

Key responsibilities:
  - Vehicle model: Defines schema with all 6 attributes (id, make, model, year, 
    price, transmission, fuel_type) per AC-001
  - fetch_vehicle(): Loads data/vehicles.json and retrieves by integer ID, 
    returns Vehicle or None per AC-002
  - JSON error handling: Catches parse/file errors and logs

This implements FR-001: System shall retrieve vehicle details by ID.
Supports AC-001 (complete Vehicle schema) and AC-002 (None on not found).

See also: app/main.py (Router), app/api/api.py (Service)
"""

from pydantic import BaseModel, ConfigDict
from typing import List, Optional
import json
import logging

logger = logging.getLogger(__name__)


class Answer(BaseModel):
    question_id: int
    alternative_id: int


class UserAnswer(BaseModel):
    user_id: int
    answers: List[Answer]


class Vehicle(BaseModel):
    """Vehicle details schema - FR-001, AC-001
    
    Attributes:
        id: Unique vehicle identifier (int)
        make: Vehicle manufacturer (str)
        model: Vehicle model name (str)
        year: Year of manufacture (int)
        price: Vehicle price in currency units (float)
        transmission: Transmission type e.g. 'automatic', 'manual' (str)
        fuel_type: Fuel/energy type e.g. 'electric', 'gasoline', 'hybrid' (str)
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "make": "Volkswagen",
                "model": "ID.3",
                "year": 2023,
                "price": 35000.0,
                "transmission": "automatic",
                "fuel_type": "electric"
            }
        }
    )
    
    id: int
    make: str
    model: str
    year: int
    price: float
    transmission: str
    fuel_type: str


def fetch_vehicle(vehicle_id: int) -> Optional[Vehicle]:
    """Load vehicles.json and search by integer ID.
    
    Maps to FR-001 (System retrieves vehicle details by ID) and AC-001.
    
    Args:
        vehicle_id: Integer vehicle ID to search for (must be > 0)
        
    Returns:
        Vehicle model instance if found, None otherwise
        
    Raises:
        Logs errors but returns None on JSON parse errors
    """
    try:
        with open('data/vehicles.json', 'r') as f:
            data = json.load(f)
            vehicles = data if isinstance(data, list) else data.get('value', [])
            
        for vehicle in vehicles:
            if vehicle.get('id') == vehicle_id:
                return Vehicle(**vehicle)
        return None
    except FileNotFoundError:
        logger.error(f"data/vehicles.json not found")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse data/vehicles.json: {e}")
        return None
    except Exception as e:
        logger.error(f"Error retrieving vehicle {vehicle_id}: {e}")
        return None