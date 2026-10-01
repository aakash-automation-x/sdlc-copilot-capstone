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