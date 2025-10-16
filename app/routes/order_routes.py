from typing import Dict

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.controllers.order_controller import OrderController
from app.database.config import get_db
from app.schemas.order_schemas import CreateOrderRequest

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=Dict)
def create_order(request: CreateOrderRequest, db: Session = Depends(get_db)):
    """
    Create a new order.

    - **title**: Order title (required)
    - **description**: Order description (optional)
    - **customer**: Customer information (optional)
    - **geo**: Order location with lat/lng (required)
    """
    return OrderController.create_order(request, db)


@router.get("/{order_id}", response_model=Dict)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """
    Get order by ID.

    Returns full order information including assigned master and ADL media if available.
    """
    return OrderController.get_order(order_id, db)


@router.post("/{order_id}/assign", response_model=Dict)
def assign_master_to_order(order_id: int, db: Session = Depends(get_db)):
    """
    Assign the best available master to an order.

    Master selection algorithm:
    1. Nearest available master (by Haversine distance)
    2. Higher rating (if distances are close)
    3. Lower current load (if ratings are close)

    Returns the updated order with assigned master information.
    """
    return OrderController.assign_master(order_id, db)


@router.post("/{order_id}/adl", response_model=Dict)
def attach_adl_to_order(order_id: int, request: Dict, db: Session = Depends(get_db)):
    """
    Attach ADL media to an order.

    Requirements:
    - **type**: Media type (photo or video) - required
    - **url**: Media URL or path - required
    - **gps**: GPS coordinates with lat/lng - required
    - **capturedAt**: ISO timestamp - required
    - **meta**: Additional metadata (optional)
    """
    from app.controllers.adl_controller import ADLController
    from app.schemas.adl_schemas import AttachADLRequest

    adl_request = AttachADLRequest(**request)
    return ADLController.attach_adl(order_id, adl_request, db)


@router.post("/{order_id}/complete", response_model=Dict)
def complete_order(order_id: int, db: Session = Depends(get_db)):
    """
    Mark an order as completed.

    Requirements:
    - Order must have valid ADL media with GPS coordinates and timestamp
    - If ADL is missing or invalid, returns 400 error

    Returns the completed order.
    """
    return OrderController.complete_order(order_id, db)
