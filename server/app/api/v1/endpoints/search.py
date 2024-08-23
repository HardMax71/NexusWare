from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from public_api import shared_schemas
from .... import crud, models
from ....api import deps

router = APIRouter()


@router.get("/products", response_model=list[shared_schemas.Product])
def search_products(
        q: str | None = Query(None, description="Search query string"),
        category_id: int | None = Query(None),
        min_price: float | None = Query(None),
        max_price: float | None = Query(None),
        in_stock: bool | None = Query(None),
        sort_by: str | None = Query(None),
        sort_order: str | None = Query("asc"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.product.advanced_search(
        db, q=q, category_id=category_id, min_price=min_price,
        max_price=max_price, in_stock=in_stock,
        sort_by=sort_by, sort_order=sort_order
    )


@router.get("/orders", response_model=list[shared_schemas.Order])
def search_orders(
        q: str | None = Query(None, description="Search query string"),
        status: str | None = Query(None),
        min_total: float | None = Query(None),
        max_total: float | None = Query(None),
        start_date: int | None = Query(None),
        end_date: int | None = Query(None),
        sort_by: str | None = Query(None),
        sort_order: str | None = Query("asc"),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.order.advanced_search(
        db, q=q, status=status, min_total=min_total,
        max_total=max_total, start_date=start_date,
        end_date=end_date, sort_by=sort_by, sort_order=sort_order
    )
