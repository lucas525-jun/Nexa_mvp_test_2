import logging
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.repositories.master_repository import MasterRepository
from app.utils.distance import haversine_distance

logger = logging.getLogger(__name__)


class MasterService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = MasterRepository(db)

    def get_all_masters(self) -> List[Dict]:
        """Get all masters with their current load"""
        masters = self.repository.get_all()
        result = []
        for master in masters:
            master_dict = master.to_dict()
            master_dict["currentLoad"] = self.repository.get_master_order_count(master.id)
            result.append(master_dict)
        return result

    def get_master_by_id(self, master_id: int) -> Optional[Dict]:
        """Get master by ID"""
        master = self.repository.get_by_id(master_id)
        if master:
            master_dict = master.to_dict()
            master_dict["currentLoad"] = self.repository.get_master_order_count(master.id)
            return master_dict
        return None

    def find_best_master(self, order_lat: float, order_lng: float) -> Optional[int]:
        """
        Find the best available master for an order based on:
        1. Nearest available master
        2. Higher rating (if distances are close)
        3. Lower current load (if ratings are close)

        Returns master_id or None if no available master found
        """
        available_masters = self.repository.get_available_masters()

        if not available_masters:
            logger.warning("No available masters found")
            return None

        # Calculate distance and load for each master
        master_candidates = []
        for master in available_masters:
            distance = haversine_distance(order_lat, order_lng, master.geo_lat, master.geo_lng)
            current_load = self.repository.get_master_order_count(master.id)

            master_candidates.append(
                {
                    "master": master,
                    "distance": distance,
                    "rating": master.rating,
                    "load": current_load,
                }
            )

            logger.info(
                f"Master {master.id} ({master.name}): "
                f"distance={distance:.2f}km, rating={master.rating}, load={current_load}"
            )

        # Sort by: distance (ascending), then rating (descending), then load (ascending)
        # This ensures: nearest → higher rating → lower load
        master_candidates.sort(key=lambda x: (x["distance"], -x["rating"], x["load"]))

        best_master = master_candidates[0]["master"]
        logger.info(
            f"Selected master {best_master.id} ({best_master.name}) "
            f"with distance={master_candidates[0]['distance']:.2f}km, "
            f"rating={best_master.rating}, load={master_candidates[0]['load']}"
        )

        return best_master.id
