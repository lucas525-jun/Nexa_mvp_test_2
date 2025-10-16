from sqlalchemy import Boolean, Column, Float, Integer, String
from sqlalchemy.orm import relationship

from app.database.base import Base


class Master(Base):
    __tablename__ = "masters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    rating = Column(Float, nullable=False, default=0.0)
    is_available = Column(Boolean, nullable=False, default=True)
    geo_lat = Column(Float, nullable=False)
    geo_lng = Column(Float, nullable=False)

    # Relationships
    orders = relationship("Order", back_populates="assigned_master")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "rating": self.rating,
            "isAvailable": self.is_available,
            "geo": {"lat": self.geo_lat, "lng": self.geo_lng},
        }
