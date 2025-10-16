import logging
from typing import Dict

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.order import OrderStatus
from app.repositories.adl_repository import ADLRepository
from app.repositories.order_repository import OrderRepository
from app.services.master_service import MasterService

logger = logging.getLogger(__name__)


class OrderService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = OrderRepository(db)
        self.adl_repository = ADLRepository(db)
        self.master_service = MasterService(db)

    def create_order(self, order_data: dict) -> Dict:
        """Create a new order"""
        order = self.repository.create(order_data)
        logger.info(f"Created order {order.id}")
        return order.to_dict()

    def get_order_by_id(self, order_id: int) -> Dict:
        """Get order by ID with all relations"""
        order = self.repository.get_by_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail=f"Order with id '{order_id}' not found")
        return order.to_dict_with_relations()

    def assign_master_to_order(self, order_id: int) -> Dict:
        """
        Assign the best available master to an order
        Selection criteria: nearest available → higher rating → lower load
        """
        # Get the order
        order = self.repository.get_by_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail=f"Order with id '{order_id}' not found")

        # Check if already assigned
        if order.assigned_master_id:
            raise HTTPException(
                status_code=400,
                detail=f"Order {order_id} is already assigned to master {order.assigned_master_id}",
            )

        # Find best master
        best_master_id = self.master_service.find_best_master(order.geo_lat, order.geo_lng)

        if not best_master_id:
            raise HTTPException(status_code=400, detail="No available masters found for assignment")

        # Assign master
        updated_order = self.repository.assign_master(order_id, best_master_id)
        logger.info(f"Assigned master {best_master_id} to order {order_id}")

        return updated_order.to_dict_with_relations()

    def complete_order(self, order_id: int) -> Dict:
        """
        Complete an order
        Requirements:
        - Order must exist
        - Order must have valid ADL (with GPS and timestamp)
        """
        # Get the order
        order = self.repository.get_by_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail=f"Order with id '{order_id}' not found")

        # Check if order already completed
        if order.status == OrderStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="Order is already completed")

        # Validate ADL exists and is valid
        if not self.adl_repository.has_valid_adl(order_id):
            raise HTTPException(
                status_code=400,
                detail="Cannot complete order: valid ADL media with GPS coordinates and timestamp is required",
            )

        # Update status to completed
        updated_order = self.repository.update_status(order_id, OrderStatus.COMPLETED)
        logger.info(f"Completed order {order_id}")

        return updated_order.to_dict_with_relations()
