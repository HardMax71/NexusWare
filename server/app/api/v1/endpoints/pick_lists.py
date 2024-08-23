# /server/app/api/v1/endpoints/pick_lists.py

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Body, Query
from sqlalchemy.orm import Session

from public_api import shared_schemas
from .... import crud, models
from ....api import deps

router = APIRouter()


@router.post("/", response_model=shared_schemas.PickList)
def create_pick_list(
        pick_list: shared_schemas.PickListCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.pick_list.create_with_items(db=db, obj_in=pick_list)


@router.get("/", response_model=List[shared_schemas.PickList])
def read_pick_lists(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        filter_params: shared_schemas.PickListFilter = Depends(),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.pick_list.get_multi_with_filter(db, skip=skip, limit=limit, filter_params=filter_params)


@router.get("/optimize_route", response_model=shared_schemas.OptimizedPickingRoute)
def optimize_picking_route(
        pick_list_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.pick_list.optimize_route(db, pick_list_id=pick_list_id)


@router.get("/performance", response_model=shared_schemas.PickingPerformance)
def get_picking_performance(
        start_date: int = Query(...),
        end_date: int = Query(...),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.pick_list.get_performance(db, start_date=start_date, end_date=end_date)


@router.get("/{pick_list_id}", response_model=shared_schemas.PickList)
def read_pick_list(
        pick_list_id: int = Path(..., title="The ID of the pick list to get"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    pick_list = crud.pick_list.get(db, id=pick_list_id)
    if pick_list is None:
        raise HTTPException(status_code=404, detail="Pick list not found")
    return pick_list


@router.put("/{pick_list_id}", response_model=shared_schemas.PickList)
def update_pick_list(
        pick_list_id: int = Path(..., title="The ID of the pick list to update"),
        pick_list_in: shared_schemas.PickListUpdate = Body(..., title="Pick list update data"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    pick_list = crud.pick_list.get(db, id=pick_list_id)
    if pick_list is None:
        raise HTTPException(status_code=404, detail="Pick list not found")
    return crud.pick_list.update_with_items(db, db_obj=pick_list, obj_in=pick_list_in)


@router.delete("/{pick_list_id}", response_model=shared_schemas.PickList)
def delete_pick_list(
        pick_list_id: int = Path(..., title="The ID of the pick list to delete"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    pick_list = crud.pick_list.get(db, id=pick_list_id)
    if pick_list is None:
        raise HTTPException(status_code=404, detail="Pick list not found")
    return crud.pick_list.remove(db, id=pick_list_id)


@router.post("/{pick_list_id}/start", response_model=shared_schemas.PickList)
def start_pick_list(
        pick_list_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.pick_list.start(db, pick_list_id=pick_list_id, user_id=current_user.id)


@router.post("/{pick_list_id}/complete", response_model=shared_schemas.PickList)
def complete_pick_list(
        pick_list_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.pick_list.complete(db, pick_list_id=pick_list_id, user_id=current_user.id)
