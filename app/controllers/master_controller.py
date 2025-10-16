from typing import Dict, List

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.config import get_db
from app.services.master_service import MasterService


class MasterController:
    @staticmethod
    def get_all_masters(db: Session = Depends(get_db)) -> List[Dict]:
        """Get all masters with their current load and availability"""
        service = MasterService(db)
        return service.get_all_masters()

    @staticmethod
    def get_master(master_id: int, db: Session = Depends(get_db)) -> Dict:
        """Get master by ID"""
        service = MasterService(db)
        return service.get_master_by_id(master_id)
