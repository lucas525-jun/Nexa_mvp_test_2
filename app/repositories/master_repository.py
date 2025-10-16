from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.master import Master


class MasterRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Master]:
        """Get all masters"""
        return self.db.query(Master).all()

    def get_by_id(self, master_id: int) -> Optional[Master]:
        """Get master by ID"""
        return self.db.query(Master).filter(Master.id == master_id).first()

    def get_available_masters(self) -> List[Master]:
        """Get all available masters"""
        return self.db.query(Master).filter(Master.is_available.is_(True)).all()

    def create(self, master_data: dict) -> Master:
        """Create new master"""
        master = Master(**master_data)
        self.db.add(master)
        self.db.commit()
        self.db.refresh(master)
        return master

    def update(self, master_id: int, master_data: dict) -> Optional[Master]:
        """Update master"""
        master = self.get_by_id(master_id)
        if master:
            for key, value in master_data.items():
                setattr(master, key, value)
            self.db.commit()
            self.db.refresh(master)
        return master

    def get_master_order_count(self, master_id: int) -> int:
        """Get count of orders assigned to a master"""
        from app.models.order import Order, OrderStatus

        return (
            self.db.query(Order)
            .filter(
                Order.assigned_master_id == master_id,
                Order.status.in_([OrderStatus.ASSIGNED, OrderStatus.IN_PROGRESS]),
            )
            .count()
        )
