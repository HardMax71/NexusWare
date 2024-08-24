# /server/app/api/v1/endpoints/customers.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .... import crud, models
from public_api import shared_schemas
from ....api import deps

router = APIRouter()


@router.post("/", response_model=shared_schemas.Customer)
def create_customer(
        customer: shared_schemas.CustomerCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.customer.create(db=db, obj_in=customer)


@router.get("/", response_model=List[shared_schemas.Customer])
def read_customers(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        customer_filter: shared_schemas.CustomerFilter = Depends(),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.customer.get_multi_with_filter(db, skip=skip, limit=limit, filter_params=customer_filter)


@router.get("/{customer_id}", response_model=shared_schemas.Customer)
def read_customer(
        customer_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    customer = crud.customer.get(db, id=customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.put("/{customer_id}", response_model=shared_schemas.Customer)
def update_customer(
        customer_id: int,
        customer_in: shared_schemas.CustomerUpdate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    customer = crud.customer.get(db, id=customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return crud.customer.update(db, db_obj=customer, obj_in=customer_in)


@router.delete("/{customer_id}", status_code=204)
def delete_customer(
        customer_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    customer = crud.customer.get(db, id=customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    crud.customer.remove(db, id=customer_id)


@router.get("/{customer_id}/orders", response_model=List[shared_schemas.Order])
def read_customer_orders(
        customer_id: int,
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_active_user)
):
    filter_params = shared_schemas.OrderFilter(customer_id=customer_id)
    return crud.order.get_multi_with_details(db, skip=skip, limit=limit, filter_params=filter_params)
