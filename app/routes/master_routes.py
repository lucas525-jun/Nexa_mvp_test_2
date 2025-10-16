from typing import Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.controllers.master_controller import MasterController
from app.database.config import get_db

router = APIRouter(prefix="/masters", tags=["Masters"])


@router.get("", response_model=List[Dict])
def get_all_masters(db: Session = Depends(get_db)):
    """
    Get all masters with their current load and availability.

    Returns:
    - List of all masters
    - Each master includes: id, name, rating, isAvailable, geo, currentLoad
    - currentLoad = number of active orders (assigned or in_progress)
    """
    return MasterController.get_all_masters(db)


@router.get("/{master_id}", response_model=Dict)
def get_master(master_id: int, db: Session = Depends(get_db)):
    """
    Get master by ID with current load information.
    """
    return MasterController.get_master(master_id, db)
