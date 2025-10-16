from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.database.config import get_db
from app.main import app
from app.models import Master

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def client():
    """Create test client with fresh database"""
    # Create tables
    Base.metadata.create_all(bind=engine)

    # Seed test masters
    db = TestingSessionLocal()
    masters = [
        Master(
            name="Test Master 1", rating=4.5, is_available=True, geo_lat=40.7128, geo_lng=-74.0060
        ),
        Master(
            name="Test Master 2", rating=4.8, is_available=True, geo_lat=40.7589, geo_lng=-73.9851
        ),
        Master(
            name="Test Master 3", rating=4.2, is_available=False, geo_lat=40.7306, geo_lng=-73.9352
        ),
    ]
    db.add_all(masters)
    db.commit()
    db.close()

    with TestClient(app) as test_client:
        yield test_client

    # Drop tables after test
    Base.metadata.drop_all(bind=engine)


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_get_all_masters(client):
    """Test getting all masters"""
    response = client.get("/api/v1/masters")
    assert response.status_code == 200
    masters = response.json()
    assert len(masters) == 3
    assert masters[0]["name"] == "Test Master 1"
    assert "currentLoad" in masters[0]


def test_create_order(client):
    """Test creating a new order"""
    order_data = {
        "title": "Test Order",
        "description": "Test description",
        "customer": {"name": "John Doe", "phone": "+1234567890"},
        "geo": {"lat": 40.7128, "lng": -74.0060},
    }
    response = client.post("/api/v1/orders", json=order_data)
    assert response.status_code == 201
    order = response.json()
    assert order["title"] == "Test Order"
    assert order["status"] == "new"
    assert order["assignedMasterId"] is None


def test_assign_master(client):
    """Test master assignment algorithm"""
    # Create order
    order_data = {"title": "Test Order", "geo": {"lat": 40.7128, "lng": -74.0060}}
    response = client.post("/api/v1/orders", json=order_data)
    order_id = response.json()["id"]

    # Assign master
    response = client.post(f"/api/v1/orders/{order_id}/assign")
    assert response.status_code == 200
    order = response.json()
    assert order["status"] == "assigned"
    assert order["assignedMasterId"] is not None
    assert "assignedMaster" in order


def test_attach_adl(client):
    """Test attaching ADL media to order"""
    # Create order
    order_data = {"title": "Test Order", "geo": {"lat": 40.7128, "lng": -74.0060}}
    response = client.post("/api/v1/orders", json=order_data)
    order_id = response.json()["id"]

    # Attach ADL
    adl_data = {
        "type": "photo",
        "url": "/test_photo.jpg",
        "gps": {"lat": 40.7128, "lng": -74.0060},
        "capturedAt": datetime.utcnow().isoformat() + "Z",
        "meta": {"device": "Test Device"},
    }
    response = client.post(f"/api/v1/orders/{order_id}/adl", json=adl_data)
    assert response.status_code == 200
    adl = response.json()
    assert adl["type"] == "photo"
    assert adl["orderId"] == order_id


def test_complete_order_without_adl_fails(client):
    """Test that completing order without ADL fails"""
    # Create order
    order_data = {"title": "Test Order", "geo": {"lat": 40.7128, "lng": -74.0060}}
    response = client.post("/api/v1/orders", json=order_data)
    order_id = response.json()["id"]

    # Try to complete without ADL
    response = client.post(f"/api/v1/orders/{order_id}/complete")
    assert response.status_code == 400
    assert "ADL" in response.json()["detail"]


def test_complete_order_with_adl_succeeds(client):
    """Test that completing order with valid ADL succeeds"""
    # Create order
    order_data = {"title": "Test Order", "geo": {"lat": 40.7128, "lng": -74.0060}}
    response = client.post("/api/v1/orders", json=order_data)
    order_id = response.json()["id"]

    # Attach ADL
    adl_data = {
        "type": "photo",
        "url": "/test_photo.jpg",
        "gps": {"lat": 40.7128, "lng": -74.0060},
        "capturedAt": datetime.utcnow().isoformat() + "Z",
    }
    client.post(f"/api/v1/orders/{order_id}/adl", json=adl_data)

    # Complete order
    response = client.post(f"/api/v1/orders/{order_id}/complete")
    assert response.status_code == 200
    order = response.json()
    assert order["status"] == "completed"


def test_get_order_not_found(client):
    """Test getting non-existent order returns 404"""
    response = client.get("/api/v1/orders/99999")
    assert response.status_code == 404
