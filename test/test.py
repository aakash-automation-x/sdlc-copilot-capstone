from starlette.testclient import TestClient
from app.main import app
from app.db.models import fetch_vehicle, Vehicle
from app.api import api
from fastapi import HTTPException
import json
import pytest

client = TestClient(app)


# ============================================================================
# EXISTING TESTS (Preserved)
# ============================================================================

def test_read_main():
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {'message': 'Fast API in Python'}


def test_read_user():
    response = client.get('/user')
    assert response.status_code == 200
    assert len(response.json()) != 0


def test_read_question():
    response = client.get('/question/1')
    assert response.status_code == 200
    assert response.json()['position'] == 1


def test_read_question_invalid():
    response = client.get('/question/0')
    assert response.status_code == 400
    assert response.json() == {'detail': 'Error'}


def test_read_alternatives():
    response = client.get('/alternatives/1')
    assert response.status_code == 200
    assert response.json()[1]['question_id'] == 1


def test_create_answer():
    body = {"user_id": 1, "answers": [{"question_id": 1, "alternative_id": 2}, {
        "question_id": 2, "alternative_id": 2}, {"question_id": 2, "alternative_id": 2}]}
    body = json.dumps(body)
    response = client.post('/answer', data=body)
    assert response.status_code == 201


def test_read_result():
    response = client.get('/result/1')
    assert response.status_code == 200


# ============================================================================
# TASK-008: Unit Tests for Data Layer (fetch_vehicle)
# Maps to FR-001, AC-001, AC-002
# ============================================================================

class TestDataLayerFetchVehicle:
    """Unit tests for fetch_vehicle() function in app/db/models.py
    
    Validates data layer retrieval logic per AC-001 (success with all attributes)
    and AC-002 (404 behavior).
    """
    
    def test_fetch_vehicle_success(self):
        """TASK-008: fetch_vehicle(1) returns Vehicle with all 6 required attributes (AC-001)"""
        vehicle = fetch_vehicle(1)
        
        # Verify Vehicle instance returned (AC-001)
        assert vehicle is not None
        assert isinstance(vehicle, Vehicle)
        
        # Verify all 6 required attributes present (AC-001)
        assert vehicle.id == 1
        assert vehicle.make == "Volkswagen"
        assert vehicle.model == "ID.3"
        assert vehicle.year == 2023
        assert vehicle.price == 35000
        assert vehicle.transmission == "automatic"
        assert vehicle.fuel_type == "electric"
    
    def test_fetch_vehicle_different_id(self):
        """TASK-008: fetch_vehicle() works for multiple vehicle IDs"""
        vehicle = fetch_vehicle(3)
        
        assert vehicle is not None
        assert vehicle.id == 3
        assert vehicle.make == "Tesla"
        assert vehicle.model == "Model 3"
        assert isinstance(vehicle.price, (int, float))
        assert vehicle.price > 0
    
    def test_fetch_vehicle_not_found(self):
        """TASK-008: fetch_vehicle(999) returns None when vehicle not found (AC-002 logic)"""
        vehicle = fetch_vehicle(999)
        
        assert vehicle is None
    
    def test_fetch_vehicle_edge_case_negative_id(self):
        """TASK-008: fetch_vehicle() handles negative IDs gracefully"""
        vehicle = fetch_vehicle(-1)
        
        # Should return None (no vehicle with negative ID exists in data)
        assert vehicle is None
    
    def test_fetch_vehicle_edge_case_zero_id(self):
        """TASK-008: fetch_vehicle() handles zero ID gracefully"""
        vehicle = fetch_vehicle(0)
        
        # Should return None (no vehicle with ID 0 exists in data)
        assert vehicle is None


# ============================================================================
# TASK-008: Unit Tests for Service Layer (get_vehicle)
# Maps to FR-001, AC-001, AC-002
# ============================================================================

class TestServiceLayerGetVehicle:
    """Unit tests for get_vehicle() function in app/api/api.py
    
    Validates service layer raises HTTPException(404) per AC-002 and
    returns Vehicle per AC-001.
    """
    
    def test_get_vehicle_success(self):
        """TASK-008: get_vehicle(1) returns Vehicle with all attributes (AC-001)"""
        vehicle = api.get_vehicle(1)
        
        assert vehicle is not None
        assert isinstance(vehicle, Vehicle)
        assert vehicle.id == 1
        assert hasattr(vehicle, 'make')
        assert hasattr(vehicle, 'model')
        assert hasattr(vehicle, 'year')
        assert hasattr(vehicle, 'price')
        assert hasattr(vehicle, 'transmission')
        assert hasattr(vehicle, 'fuel_type')
    
    def test_get_vehicle_not_found_raises_404(self):
        """TASK-008: get_vehicle(999) raises HTTPException(404) (AC-002)"""
        with pytest.raises(HTTPException) as exc_info:
            api.get_vehicle(999)
        
        assert exc_info.value.status_code == 404
        assert "Vehicle not found" in exc_info.value.detail
    
    def test_get_vehicle_multiple_ids(self):
        """TASK-008: get_vehicle() retrieves different vehicles correctly"""
        v1 = api.get_vehicle(1)
        v5 = api.get_vehicle(5)
        
        assert v1.id == 1
        assert v5.id == 5
        assert v1.make != v5.make  # Different vehicles


# ============================================================================
# TASK-009: Integration Tests for FastAPI Endpoint
# Maps to FR-001, AC-001, AC-002; complete AC coverage
# ============================================================================

class TestVehicleEndpointIntegration:
    """Integration tests for GET /vehicles/{vehicle_id} endpoint using TestClient
    
    Validates end-to-end flow from HTTP request through service/data layers
    per AC-001 (HTTP 200 + all 6 attributes) and AC-002 (HTTP 404).
    """
    
    def test_get_vehicle_endpoint_success_ac001(self):
        """TASK-009: GET /vehicles/1 returns HTTP 200 with all 6 attributes (AC-001)"""
        response = client.get('/vehicles/1')
        
        # HTTP 200 success (AC-001)
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify all 6 required attributes present in response (AC-001)
        required_attrs = ['id', 'make', 'model', 'year', 'price', 'transmission', 'fuel_type']
        for attr in required_attrs:
            assert attr in data, f"Missing required attribute: {attr}"
        
        # Verify correct vehicle returned
        assert data['id'] == 1
        assert data['make'] == 'Volkswagen'
        assert data['model'] == 'ID.3'
        assert data['year'] == 2023
        assert isinstance(data['price'], (int, float))
        assert data['transmission'] == 'automatic'
        assert data['fuel_type'] == 'electric'
    
    def test_get_vehicle_endpoint_different_vehicle(self):
        """TASK-009: GET /vehicles/{id} returns correct vehicle data for different IDs"""
        response = client.get('/vehicles/3')
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['id'] == 3
        assert data['make'] == 'Tesla'
        assert data['model'] == 'Model 3'
    
    def test_get_vehicle_endpoint_not_found_ac002(self):
        """TASK-009: GET /vehicles/999 returns HTTP 404 with error message (AC-002)"""
        response = client.get('/vehicles/999')
        
        # HTTP 404 not found (AC-002)
        assert response.status_code == 404
        
        data = response.json()
        
        # Verify error detail present (AC-002)
        assert 'detail' in data
        assert 'not found' in data['detail'].lower() or 'not found' in str(data).lower()
    
    def test_get_vehicle_endpoint_invalid_string_id(self):
        """TASK-009: GET /vehicles/abc returns HTTP 422 validation error"""
        response = client.get('/vehicles/abc')
        
        # FastAPI validation error
        assert response.status_code == 422
    
    def test_get_vehicle_endpoint_invalid_zero_id(self):
        """TASK-009: GET /vehicles/0 returns HTTP 422 validation error (gt=0 constraint)"""
        response = client.get('/vehicles/0')
        
        # FastAPI validation error for Path(gt=0)
        assert response.status_code == 422
    
    def test_get_vehicle_endpoint_invalid_negative_id(self):
        """TASK-009: GET /vehicles/-1 returns HTTP 422 validation error (gt=0 constraint)"""
        response = client.get('/vehicles/-1')
        
        # FastAPI validation error for Path(gt=0)
        assert response.status_code == 422
    
    def test_get_vehicle_endpoint_all_attributes_populated(self):
        """TASK-009: Response includes all 6 attributes with valid types (AC-001)"""
        response = client.get('/vehicles/5')
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify types
        assert isinstance(data['id'], int)
        assert isinstance(data['make'], str)
        assert isinstance(data['model'], str)
        assert isinstance(data['year'], int)
        assert isinstance(data['price'], (int, float))
        assert isinstance(data['transmission'], str)
        assert isinstance(data['fuel_type'], str)
        
        # Verify non-empty
        assert len(data['make']) > 0
        assert len(data['model']) > 0
        assert len(data['transmission']) > 0
        assert len(data['fuel_type']) > 0
