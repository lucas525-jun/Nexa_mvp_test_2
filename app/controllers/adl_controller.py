from typing import Dict

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.config import get_db
from app.schemas.adl_schemas import AttachADLRequest
from app.services.adl_service import ADLService


class ADLController:
    @staticmethod
    def attach_adl(order_id: int, request: AttachADLRequest, db: Session = Depends(get_db)) -> Dict:
        """Attach ADL media to an order"""
        adl_data = {
            "type": request.type,
            "url": request.url,
            "gps_lat": request.gps.get("lat"),
            "gps_lng": request.gps.get("lng"),
            "captured_at": request.capturedAt,
            "meta": request.meta,
        }
        service = ADLService(db)
        return service.attach_adl_to_order(order_id, adl_data)
