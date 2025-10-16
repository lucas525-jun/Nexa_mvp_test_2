import logging
from typing import Dict

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.adl_repository import ADLRepository
from app.repositories.order_repository import OrderRepository

logger = logging.getLogger(__name__)


class ADLService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = ADLRepository(db)
        self.order_repository = OrderRepository(db)

    def attach_adl_to_order(self, order_id: int, adl_data: dict) -> Dict:
        """
        Attach ADL media to an order
        Validates that:
        - Order exists
        - GPS coordinates are provided
        - Timestamp is provided
        """
        # Check if order exists
        order = self.order_repository.get_by_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail=f"Order with id '{order_id}' not found")

        # Validate GPS coordinates
        if adl_data.get("gps_lat") is None or adl_data.get("gps_lng") is None:
            raise HTTPException(
                status_code=400, detail="GPS coordinates (gps_lat, gps_lng) are required"
            )

        # Validate timestamp
        if adl_data.get("captured_at") is None:
            raise HTTPException(
                status_code=400, detail="Timestamp (captured_at) is required in ISO format"
            )

        # Add order_id to adl_data
        adl_data["order_id"] = order_id

        # Create ADL media
        adl = self.repository.create(adl_data)
        logger.info(f"Attached ADL {adl.id} to order {order_id}")

        return adl.to_dict()
