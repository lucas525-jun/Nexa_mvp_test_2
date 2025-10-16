import enum

from sqlalchemy import JSON, Column, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database.base import Base


class MediaType(str, enum.Enum):
    PHOTO = "photo"
    VIDEO = "video"


class ADLMedia(Base):
    __tablename__ = "adl_media"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    type = Column(SQLEnum(MediaType), nullable=False)
    url = Column(String, nullable=False)  # path or URL to media
    gps_lat = Column(Float, nullable=False)
    gps_lng = Column(Float, nullable=False)
    captured_at = Column(DateTime, nullable=False)  # ISO timestamp
    meta = Column(JSON, nullable=True)  # Additional metadata

    # Relationships
    order = relationship("Order", back_populates="adl_media")

    def to_dict(self):
        return {
            "id": self.id,
            "orderId": self.order_id,
            "type": self.type.value,
            "url": self.url,
            "gps": {"lat": self.gps_lat, "lng": self.gps_lng},
            "capturedAt": self.captured_at.isoformat() if self.captured_at else None,
            "meta": self.meta,
        }
