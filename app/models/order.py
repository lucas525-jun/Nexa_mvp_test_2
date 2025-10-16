import enum
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database.base import Base


class OrderStatus(str, enum.Enum):
    NEW = "new"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(SQLEnum(OrderStatus), nullable=False, default=OrderStatus.NEW)
    customer = Column(JSON, nullable=True)  # {name: str, phone: str}
    geo_lat = Column(Float, nullable=False)
    geo_lng = Column(Float, nullable=False)
    assigned_master_id = Column(Integer, ForeignKey("masters.id"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assigned_master = relationship("Master", back_populates="orders")
    adl_media = relationship("ADLMedia", back_populates="order", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "customer": self.customer,
            "geo": {"lat": self.geo_lat, "lng": self.geo_lng},
            "assignedMasterId": self.assigned_master_id,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }

    def to_dict_with_relations(self):
        result = self.to_dict()
        if self.assigned_master:
            result["assignedMaster"] = self.assigned_master.to_dict()
        if self.adl_media:
            result["adlMedia"] = [adl.to_dict() for adl in self.adl_media]
        return result
