from typing import Dict

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.config import get_db
from app.schemas.order_schemas import CreateOrderRequest
from app.services.order_service import OrderService


class OrderController:
    @staticmethod
    def create_order(request: CreateOrderRequest, db: Session = Depends(get_db)) -> Dict:
        """Create a new order"""
        order_data = {
            "title": request.title,
            "description": request.description,
            "customer": request.customer.dict() if request.customer else None,
            "geo_lat": request.geo.lat,
            "geo_lng": request.geo.lng,
        }
        service = OrderService(db)
        return service.create_order(order_data)

    @staticmethod
    def get_order(order_id: int, db: Session = Depends(get_db)) -> Dict:
        """Get order by ID"""
        service = OrderService(db)
        return service.get_order_by_id(order_id)

    @staticmethod
    def assign_master(order_id: int, db: Session = Depends(get_db)) -> Dict:
        """Assign master to order"""
        service = OrderService(db)
        return service.assign_master_to_order(order_id)

    @staticmethod
    def complete_order(order_id: int, db: Session = Depends(get_db)) -> Dict:
        """Complete an order"""
        service = OrderService(db)
        return service.complete_order(order_id)
