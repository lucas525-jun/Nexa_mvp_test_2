from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.order import Order, OrderStatus


class OrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Order]:
        """Get all orders"""
        return self.db.query(Order).all()

    def get_by_id(self, order_id: int) -> Optional[Order]:
        """Get order by ID"""
        return self.db.query(Order).filter(Order.id == order_id).first()

    def create(self, order_data: dict) -> Order:
        """Create new order"""
        order = Order(**order_data)
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return order

    def update(self, order_id: int, order_data: dict) -> Optional[Order]:
        """Update order"""
        order = self.get_by_id(order_id)
        if order:
            for key, value in order_data.items():
                setattr(order, key, value)
            self.db.commit()
            self.db.refresh(order)
        return order

    def assign_master(self, order_id: int, master_id: int) -> Optional[Order]:
        """Assign master to order"""
        return self.update(
            order_id, {"assigned_master_id": master_id, "status": OrderStatus.ASSIGNED}
        )

    def update_status(self, order_id: int, status: OrderStatus) -> Optional[Order]:
        """Update order status"""
        return self.update(order_id, {"status": status})
