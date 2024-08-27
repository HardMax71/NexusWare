from public_api.shared_schemas import (
    PickListCreate, PickListUpdate, PickList, PickListFilter,
    OptimizedPickingRoute, PickingPerformance
)
from .client import APIClient


class PickListsAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def create_pick_list(self, pick_list_data: PickListCreate) -> PickList:
        response = self.client.post("/pick_lists/", json=pick_list_data.model_dump(mode="json"))
        return PickList.model_validate(response)

    def get_pick_lists(self, skip: int = 0, limit: int = 100,
                       filter_params: PickListFilter | None = None) -> list[PickList]:
        params = {"skip": skip, "limit": limit}
        if filter_params:
            params.update(filter_params.model_dump(mode="json", exclude_unset=True))
        response = self.client.get("/pick_lists/", params=params)
        return [PickList.model_validate(item) for item in response]

    def get_pick_list(self, pick_list_id: int) -> PickList:
        response = self.client.get(f"/pick_lists/{pick_list_id}")
        return PickList.model_validate(response)

    def update_pick_list(self, pick_list_id: int, pick_list_data: PickListUpdate) -> PickList:
        response = self.client.put(f"/pick_lists/{pick_list_id}",
                                   json=pick_list_data.model_dump(mode="json", exclude_unset=True))
        return PickList.model_validate(response)

    def delete_pick_list(self, pick_list_id: int) -> None:
        self.client.delete(f"/pick_lists/{pick_list_id}")

    def optimize_picking_route(self, pick_list_id: int) -> OptimizedPickingRoute:
        response = self.client.get("/pick_lists/optimize_route", params={"pick_list_id": pick_list_id})
        return OptimizedPickingRoute.model_validate(response)

    def start_pick_list(self, pick_list_id: int) -> PickList:
        response = self.client.post(f"/pick_lists/{pick_list_id}/start")
        return PickList.model_validate(response)

    def complete_pick_list(self, pick_list_id: int) -> PickList:
        response = self.client.post(f"/pick_lists/{pick_list_id}/complete")
        return PickList.model_validate(response)

    def get_picking_performance(self, start_date: int, end_date: int) -> PickingPerformance:
        params = {
            "start_date": start_date,
            "end_date": end_date
        }
        response = self.client.get("/pick_lists/performance", params=params)
        return PickingPerformance.model_validate(response)
