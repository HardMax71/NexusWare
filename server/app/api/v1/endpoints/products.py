# /server/app/api/v1/endpoints/products.py

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session, joinedload

from public_api import shared_schemas
from .... import crud, models
from ....api import deps
from ....models import Product

router = APIRouter()


@router.post("/", response_model=shared_schemas.Product)
def create_product(
        product: shared_schemas.ProductCreate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.product.create(db=db, obj_in=product)


@router.get("/", response_model=list[shared_schemas.ProductWithCategoryAndInventory])
def read_products(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        product_filter: shared_schemas.ProductFilter = Depends(),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.product.get_multi_with_category_and_inventory(db, skip=skip, limit=limit, filter_params=product_filter)


@router.get("/max_id", response_model=int)
def get_max_product_id(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.product.get_max_id(db)


@router.post("/barcode", response_model=shared_schemas.Product)
def get_product_by_barcode(
        barcode_data: shared_schemas.BarcodeData,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    options = [
        joinedload(Product.category),
        joinedload(Product.inventory_items)
    ]

    product = crud.product.get(db, barcode=barcode_data.barcode, options=options)

    if product:
        return product
    raise HTTPException(status_code=404, detail="Product not found")


@router.get("/{product_id}", response_model=shared_schemas.ProductWithCategoryAndInventory)
def read_product(
        product_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    options = [
        joinedload(Product.category),
        joinedload(Product.inventory_items)
    ]

    product = crud.product.get(db, id=product_id, options=options)

    if product:
        return product
    raise HTTPException(status_code=404, detail="Product not found")


@router.put("/{product_id}", response_model=shared_schemas.Product)
def update_product(
        product_id: int,
        product_in: shared_schemas.ProductUpdate,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    product = crud.product.get(db, id=product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return crud.product.update(db, db_obj=product, obj_in=product_in)


@router.delete("/{product_id}", status_code=204)
def delete_product(
        product_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_admin)
):
    product = crud.product.get(db, id=product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    crud.product.remove(db, id=product_id)


@router.get("/{product_id}/substitutes", response_model=list[shared_schemas.Product])
def get_product_substitutes(
        product_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.product.get_substitutes(db, product_id=product_id)


@router.post("/{product_id}/substitutes", response_model=shared_schemas.Product)
def add_product_substitute(
        product_id: int,
        substitute_id: int = Body(..., embed=True),
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user)
):
    return crud.product.add_substitute(db, product_id=product_id, substitute_id=substitute_id)
