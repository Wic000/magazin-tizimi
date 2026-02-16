"""Mahsulotlar API"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models import Product, User
from schemas import ProductCreate, ProductUpdate, ProductResponse
from auth import get_current_user, require_admin

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[ProductResponse])
def list_products(
    active_only: bool = Query(True, description="Faqat faol mahsulotlar"),
    search: str = Query(""),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    q = db.query(Product)
    if active_only:
        q = q.filter(Product.is_active == True)
    if search:
        q = q.filter(Product.name.ilike(f"%{search}%"))
    return q.order_by(Product.name).all()


@router.post("", response_model=ProductResponse)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin)
):
    product = Product(**data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("/{id}", response_model=ProductResponse)
def get_product(
    id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    p = db.query(Product).filter(Product.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Mahsulot topilmadi")
    return p


@router.patch("/{id}", response_model=ProductResponse)
def update_product(
    id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin)
):
    p = db.query(Product).filter(Product.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Mahsulot topilmadi")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(p, k, v)
    db.commit()
    db.refresh(p)
    return p


@router.post("/{id}/archive")
def archive_product(
    id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin)
):
    p = db.query(Product).filter(Product.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Mahsulot topilmadi")
    p.is_active = False
    db.commit()
    return {"ok": True}


@router.post("/{id}/restore")
def restore_product(
    id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin)
):
    p = db.query(Product).filter(Product.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Mahsulot topilmadi")
    p.is_active = True
    db.commit()
    return {"ok": True}
