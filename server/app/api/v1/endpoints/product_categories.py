# /server/app/api/v1/endpoints/product_categories.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models
from app.api import deps
from public_api import shared_schemas

router = APIRouter()


@router.post("/", response_model=shared_schemas.ProductCategory)
def create_category(
        category: shared_schemas.ProductCategoryCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.product_category.create(db=db, obj_in=category)


@router.get("/", response_model=list[shared_schemas.ProductCategory])
def read_categories(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.product_category.get_multi(db, skip=skip, limit=limit)


@router.get("/{category_id}", response_model=shared_schemas.ProductCategory)
def read_category(
        category_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    category = crud.product_category.get(db, id=category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.put("/{category_id}", response_model=shared_schemas.ProductCategory)
def update_category(
        category_id: int,
        category_in: shared_schemas.ProductCategoryUpdate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    category = crud.product_category.get(db, id=category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return crud.product_category.update(db, db_obj=category, obj_in=category_in)


@router.delete("/{category_id}", status_code=204)
def delete_category(
        category_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    category = crud.product_category.get(db, id=category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    crud.product_category.remove(db, id=category_id)
