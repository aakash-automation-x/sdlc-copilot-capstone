import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from starlette.testclient import TestClient

from app.main import app
from app.db.database import get_db, Base
from app.db.models import Vehicle

SQLALCHEMY_TEST_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    vehicle = Vehicle(
        id=1,
        make="Toyota",
        model="Corolla",
        year=2022,
        price=24999.99,
        transmission="automatic",
        fuel_type="petrol",
    )
    db.add(vehicle)
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


def test_get_vehicle_by_id_success():
    """FR-001 / AC-001: all six attributes returned for a valid vehicle ID."""
    response = client.get("/vehicles/1")
    assert response.status_code == 200
    data = response.json()
    assert data["make"] == "Toyota"
    assert data["model"] == "Corolla"
    assert data["year"] == 2022
    assert data["price"] == pytest.approx(24999.99)
    assert data["transmission"] == "automatic"
    assert data["fuel_type"] == "petrol"
    assert "id" not in data


def test_get_vehicle_by_id_not_found():
    """FR-001 / AC-002: 404 returned when vehicle ID does not exist."""
    response = client.get("/vehicles/9999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Vehicle not found"}


def test_get_vehicle_content_type():
    """AC-003: response Content-Type is application/json."""
    response = client.get("/vehicles/1")
    assert response.headers["content-type"].startswith("application/json")
