from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.adl_media import ADLMedia


class ADLRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_order_id(self, order_id: int) -> List[ADLMedia]:
        """Get all ADL media for an order"""
        return self.db.query(ADLMedia).filter(ADLMedia.order_id == order_id).all()

    def get_by_id(self, adl_id: int) -> Optional[ADLMedia]:
        """Get ADL media by ID"""
        return self.db.query(ADLMedia).filter(ADLMedia.id == adl_id).first()

    def create(self, adl_data: dict) -> ADLMedia:
        """Create new ADL media"""
        adl = ADLMedia(**adl_data)
        self.db.add(adl)
        self.db.commit()
        self.db.refresh(adl)
        return adl

    def has_valid_adl(self, order_id: int) -> bool:
        """Check if order has at least one valid ADL with GPS and timestamp"""
        adl_list = self.get_by_order_id(order_id)
        if not adl_list:
            return False

        # Check if at least one ADL has valid GPS coordinates and timestamp
        for adl in adl_list:
            if adl.gps_lat is not None and adl.gps_lng is not None and adl.captured_at is not None:
                return True
        return False
