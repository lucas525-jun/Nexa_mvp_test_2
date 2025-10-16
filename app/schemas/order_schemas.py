from typing import Dict, Optional

from pydantic import BaseModel, Field


class GeoLocation(BaseModel):
    lat: float = Field(..., description="Latitude")
    lng: float = Field(..., description="Longitude")


class CustomerInfo(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None


class CreateOrderRequest(BaseModel):
    title: str = Field(..., description="Order title")
    description: Optional[str] = Field(None, description="Order description")
    customer: Optional[CustomerInfo] = Field(None, description="Customer information")
    geo: GeoLocation = Field(..., description="Order location")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Fix plumbing issue",
                "description": "Kitchen sink is leaking",
                "customer": {"name": "John Doe", "phone": "+1234567890"},
                "geo": {"lat": 40.7128, "lng": -74.0060},
            }
        }


class OrderResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    customer: Optional[Dict]
    geo: Dict
    assignedMasterId: Optional[int]
    createdAt: str
    updatedAt: str

    class Config:
        from_attributes = True
