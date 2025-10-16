from datetime import datetime
from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel, Field


class MediaTypeEnum(str, Enum):
    PHOTO = "photo"
    VIDEO = "video"


class AttachADLRequest(BaseModel):
    type: MediaTypeEnum = Field(..., description="Type of media (photo or video)")
    url: str = Field(..., description="URL or path to the media file")
    gps: Dict[str, float] = Field(..., description="GPS coordinates where media was captured")
    capturedAt: datetime = Field(..., description="ISO timestamp when media was captured")
    meta: Optional[Dict] = Field(None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "type": "photo",
                "url": "/uploads/order_123_photo1.jpg",
                "gps": {"lat": 40.7128, "lng": -74.0060},
                "capturedAt": "2025-10-16T14:30:00Z",
                "meta": {"device": "iPhone 14", "fileSize": "2.5MB"},
            }
        }


class ADLResponse(BaseModel):
    id: int
    orderId: int
    type: str
    url: str
    gps: Dict
    capturedAt: str
    meta: Optional[Dict]

    class Config:
        from_attributes = True
