"""
Test suite for GET /vehicles/{vehicle_id} - FR-001, AC-001.

Uses an in-memory SQLite database via a get_db dependency override so no
running server or real database is required.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from starlette.testclient import TestClient

from app.main import app
from app.db.database import get_db, Base
from app.db.models import Vehicle

# In-memory SQLite engine for test isolation - TASK-008.
# StaticPool ensures all sessions share the same underlying connection so the
# schema created by the fixture is visible to the TestClient's request thread.
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Replace the production get_db with one backed by the in-memory engine."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Create schema, seed one Vehicle row, run the test, then tear down."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        test_vehicle = Vehicle(
            id=1,
            make="Toyota",
            model="Corolla",
            year=2022,
            price="25000",
            transmission="automatic",
            fuel_type="petrol",
        )
        db.add(test_vehicle)
        db.commit()
    finally:
        db.close()
    yield
    Base.metadata.drop_all(bind=engine)


def test_get_vehicle_by_id_success():
    """GET /vehicles/1 returns HTTP 200 with all six vehicle fields - AC-001."""
    response = client.get("/vehicles/1")
    assert response.status_code == 200
    data = response.json()
    assert data["make"] == "Toyota"
    assert data["model"] == "Corolla"
    assert data["year"] == 2022
    assert data["price"] == "25000"
    assert data["transmission"] == "automatic"
    assert data["fuel_type"] == "petrol"


def test_get_vehicle_by_id_not_found():
    """GET /vehicles/9999 returns HTTP 404 - FR-001."""
    response = client.get("/vehicles/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Vehicle not found"
