# /server/app/api/v1/endpoints/search.py
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from .... import crud, models, schemas
from ....api import deps

router = APIRouter()


@router.get("/products", response_model=List[schemas.Product])
def search_products(
        q: Optional[str] = Query(None, description="Search query string"),
        category_id: Optional[int] = Query(None),
        min_price: Optional[float] = Query(None),
        max_price: Optional[float] = Query(None),
        in_stock: Optional[bool] = Query(None),
        sort_by: Optional[str] = Query(None),
        sort_order: Optional[str] = Query("asc"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.product.advanced_search(
        db, q=q, category_id=category_id, min_price=min_price,
        max_price=max_price, in_stock=in_stock,
        sort_by=sort_by, sort_order=sort_order
    )


@router.get("/orders", response_model=List[schemas.Order])
def search_orders(
        q: Optional[str] = Query(None, description="Search query string"),
        status: Optional[str] = Query(None),
        min_total: Optional[float] = Query(None),
        max_total: Optional[float] = Query(None),
        start_date: Optional[date] = Query(None),
        end_date: Optional[date] = Query(None),
        sort_by: Optional[str] = Query(None),
        sort_order: Optional[str] = Query("asc"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.order.advanced_search(
        db, q=q, status=status, min_total=min_total,
        max_total=max_total, start_date=start_date,
        end_date=end_date, sort_by=sort_by, sort_order=sort_order
    )
