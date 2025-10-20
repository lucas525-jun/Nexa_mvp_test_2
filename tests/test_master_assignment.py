"""
Unit tests for master assignment algorithm - tests tie-break logic:
1. Nearest distance wins
2. Higher rating wins when distances are close
3. Lower load wins when ratings are close
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.models import Master, Order
from app.models.order import OrderStatus
from app.services.master_service import MasterService

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_master_assignment.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


def test_assignment_nearest_distance_wins(db_session):
    """Test that nearest master is selected when all else is equal"""
    # Create masters at different distances from order location (40.7128, -74.0060)
    masters = [
        Master(
            name="Far Master",
            rating=4.5,
            is_available=True,
            geo_lat=40.8000,  # Further away
            geo_lng=-74.0000,
        ),
        Master(
            name="Near Master",
            rating=4.5,
            is_available=True,
            geo_lat=40.7130,  # Very close to order
            geo_lng=-74.0061,
        ),
        Master(
            name="Mid Master",
            rating=4.5,
            is_available=True,
            geo_lat=40.7500,  # Mid distance
            geo_lng=-74.0000,
        ),
    ]
    db_session.add_all(masters)
    db_session.commit()

    service = MasterService(db_session)
    best_master_id = service.find_best_master(40.7128, -74.0060)

    # Should select the nearest master (Near Master)
    selected_master = db_session.query(Master).filter(Master.id == best_master_id).first()
    assert selected_master.name == "Near Master"


def test_assignment_rating_breaks_tie(db_session):
    """Test that higher rating wins when distances are exactly the same"""
    # Create masters at EXACTLY the same location but different ratings
    # Order location: 40.7128, -74.0060
    masters = [
        Master(
            name="Master Low Rating",
            rating=4.2,
            is_available=True,
            geo_lat=40.7500,  # Same location for all
            geo_lng=-74.0000,
        ),
        Master(
            name="Master High Rating",
            rating=4.9,
            is_available=True,
            geo_lat=40.7500,  # Same location for all
            geo_lng=-74.0000,
        ),
        Master(
            name="Master Mid Rating",
            rating=4.5,
            is_available=True,
            geo_lat=40.7500,  # Same location for all
            geo_lng=-74.0000,
        ),
    ]
    db_session.add_all(masters)
    db_session.commit()

    service = MasterService(db_session)
    best_master_id = service.find_best_master(40.7128, -74.0060)

    # Should select the master with highest rating when distance is equal
    selected_master = db_session.query(Master).filter(Master.id == best_master_id).first()
    assert selected_master.name == "Master High Rating"
    assert selected_master.rating == 4.9


def test_assignment_load_breaks_tie(db_session):
    """Test that lower load wins when distance and rating are exactly the same"""
    # Create masters with EXACTLY same location and rating but different loads
    masters = [
        Master(
            name="Master Heavy Load",
            rating=4.8,
            is_available=True,
            geo_lat=40.7500,  # Exact same location
            geo_lng=-74.0000,
        ),
        Master(
            name="Master Light Load",
            rating=4.8,
            is_available=True,
            geo_lat=40.7500,  # Exact same location
            geo_lng=-74.0000,
        ),
    ]
    db_session.add_all(masters)
    db_session.commit()

    # Add orders to create different loads
    # Give Heavy Load master 3 orders
    for i in range(3):
        order = Order(
            title=f"Order {i}",
            status=OrderStatus.ASSIGNED,
            geo_lat=40.7128,
            geo_lng=-74.0060,
            assigned_master_id=masters[0].id,
        )
        db_session.add(order)

    # Give Light Load master 1 order
    order = Order(
        title="Single Order",
        status=OrderStatus.ASSIGNED,
        geo_lat=40.7128,
        geo_lng=-74.0060,
        assigned_master_id=masters[1].id,
    )
    db_session.add(order)
    db_session.commit()

    service = MasterService(db_session)
    best_master_id = service.find_best_master(40.7128, -74.0060)

    # Should select the master with lower load when distance and rating are equal
    selected_master = db_session.query(Master).filter(Master.id == best_master_id).first()
    assert selected_master.name == "Master Light Load"


def test_assignment_only_available_masters(db_session):
    """Test that unavailable masters are not selected"""
    masters = [
        Master(
            name="Unavailable Master",
            rating=5.0,
            is_available=False,  # Not available
            geo_lat=40.7128,  # Closest
            geo_lng=-74.0060,
        ),
        Master(
            name="Available Master",
            rating=4.0,
            is_available=True,
            geo_lat=40.7500,  # Further but available
            geo_lng=-74.0000,
        ),
    ]
    db_session.add_all(masters)
    db_session.commit()

    service = MasterService(db_session)
    best_master_id = service.find_best_master(40.7128, -74.0060)

    # Should select the available master, not the unavailable one
    selected_master = db_session.query(Master).filter(Master.id == best_master_id).first()
    assert selected_master.name == "Available Master"
    assert selected_master.is_available is True


def test_assignment_no_available_masters(db_session):
    """Test that None is returned when no masters are available"""
    masters = [
        Master(
            name="Unavailable 1",
            rating=4.5,
            is_available=False,
            geo_lat=40.7128,
            geo_lng=-74.0060,
        ),
        Master(
            name="Unavailable 2",
            rating=4.8,
            is_available=False,
            geo_lat=40.7500,
            geo_lng=-74.0000,
        ),
    ]
    db_session.add_all(masters)
    db_session.commit()

    service = MasterService(db_session)
    best_master_id = service.find_best_master(40.7128, -74.0060)

    # Should return None when no available masters
    assert best_master_id is None


def test_assignment_complete_tiebreak_scenario(db_session):
    """Test complete tie-break scenario: distance → rating → load"""
    # Master 1: Far but high rating and low load
    # Master 2: Same close location, same high rating, high load
    # Master 3: Same close location, same high rating, low load - SHOULD WIN
    masters = [
        Master(
            name="Far High Rating Low Load",
            rating=4.9,
            is_available=True,
            geo_lat=40.8000,  # Far
            geo_lng=-74.0000,
        ),
        Master(
            name="Close High Rating High Load",
            rating=4.9,
            is_available=True,
            geo_lat=40.7500,  # Close - exact same location as master 3
            geo_lng=-74.0000,
        ),
        Master(
            name="Close High Rating Low Load",
            rating=4.9,
            is_available=True,
            geo_lat=40.7500,  # Close - exact same location as master 2
            geo_lng=-74.0000,
        ),
    ]
    db_session.add_all(masters)
    db_session.commit()

    # Give master 2 (index 1) more load
    for i in range(5):
        order = Order(
            title=f"Order {i}",
            status=OrderStatus.ASSIGNED,
            geo_lat=40.7128,
            geo_lng=-74.0060,
            assigned_master_id=masters[1].id,
        )
        db_session.add(order)

    # Give master 3 (index 2) less load
    order = Order(
        title="Single Order",
        status=OrderStatus.ASSIGNED,
        geo_lat=40.7128,
        geo_lng=-74.0060,
        assigned_master_id=masters[2].id,
    )
    db_session.add(order)
    db_session.commit()

    service = MasterService(db_session)
    best_master_id = service.find_best_master(40.7128, -74.0060)

    # Should select close master with high rating and low load (not the far one)
    selected_master = db_session.query(Master).filter(Master.id == best_master_id).first()
    # First criteria: distance (so not "Far High Rating Low Load")
    assert selected_master.name != "Far High Rating Low Load"
    # When distance and rating are equal, lower load wins
    assert selected_master.name == "Close High Rating Low Load"
