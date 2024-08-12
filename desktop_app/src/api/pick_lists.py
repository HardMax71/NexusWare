from datetime import datetime
from typing import Optional

from .client import APIClient


class PickListsAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def create_pick_list(self, pick_list_data: dict):
        return self.client.post("/pick_lists/", json=pick_list_data)

    def get_pick_lists(self, skip: int = 0, limit: int = 100, filter_params: Optional[dict] = None):
        return self.client.get("/pick_lists/", params={"skip": skip, "limit": limit, **(filter_params or {})})

    def get_pick_list(self, pick_list_id: int):
        return self.client.get(f"/pick_lists/{pick_list_id}")

    def update_pick_list(self, pick_list_id: int, pick_list_data: dict):
        return self.client.put(f"/pick_lists/{pick_list_id}", json=pick_list_data)

    def delete_pick_list(self, pick_list_id: int):
        return self.client.delete(f"/pick_lists/{pick_list_id}")

    def optimize_picking_route(self, pick_list_id: int):
        return self.client.get(f"/pick_lists/optimize_route?pick_list_id={pick_list_id}")

    def start_pick_list(self, pick_list_id: int):
        return self.client.post(f"/pick_lists/{pick_list_id}/start")

    def complete_pick_list(self, pick_list_id: int):
        return self.client.post(f"/pick_lists/{pick_list_id}/complete")

    def get_picking_performance(self, start_date: datetime, end_date: datetime):
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
        return self.client.get("/pick_lists/performance", params=params)
