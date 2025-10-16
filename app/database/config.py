import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database.base import Base

logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./nexa_test2.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})  # Needed for SQLite

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


def seed_sample_data():
    """Seed database with sample masters for testing"""
    from app.models import Master

    db = SessionLocal()
    try:
        # Check if masters already exist
        if db.query(Master).count() > 0:
            logger.info("Sample data already exists, skipping seed")
            return

        # Create sample masters
        masters = [
            Master(
                name="John Smith", rating=4.5, is_available=True, geo_lat=40.7128, geo_lng=-74.0060
            ),
            Master(
                name="Maria Garcia",
                rating=4.8,
                is_available=True,
                geo_lat=40.7589,
                geo_lng=-73.9851,
            ),
            Master(
                name="Ahmed Hassan",
                rating=4.2,
                is_available=True,
                geo_lat=40.7306,
                geo_lng=-73.9352,
            ),
            Master(
                name="Li Wei", rating=4.9, is_available=False, geo_lat=40.7489, geo_lng=-73.9680
            ),
            Master(
                name="Sarah Johnson",
                rating=4.6,
                is_available=True,
                geo_lat=40.7580,
                geo_lng=-73.9855,
            ),
        ]

        db.add_all(masters)
        db.commit()
        logger.info(f"Seeded {len(masters)} sample masters")
    except Exception as e:
        logger.error(f"Error seeding sample data: {e}")
        db.rollback()
    finally:
        db.close()
