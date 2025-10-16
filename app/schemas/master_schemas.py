from typing import Dict

from pydantic import BaseModel, Field


class MasterResponse(BaseModel):
    id: int
    name: str
    rating: float
    isAvailable: bool
    geo: Dict
    currentLoad: int = Field(..., description="Number of active orders assigned to this master")

    class Config:
        from_attributes = True
