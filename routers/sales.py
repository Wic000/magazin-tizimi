"""Sotuvlar API"""
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import Product, Sale, SaleItem, User
from schemas import SaleCreate, SaleResponse, SaleItemResponse
from auth import get_current_user

router = APIRouter(prefix="/sales", tags=["sales"])


@router.post("", response_model=SaleResponse)
def create_sale(
    data: SaleCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    sale = Sale(user_id=user.id, total_amount=0, total_profit=0)
    db.add(sale)
    db.flush()
    total_amount = 0.0
    total_profit = 0.0
    for item in data.items:
        product = db.query(Product).filter(Product.id == item.product_id, Product.is_active == True).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Mahsulot ID={item.product_id} topilmadi")
        if product.quantity < item.quantity:
            raise HTTPException(status_code=400, detail=f"'{product.name}' uchun yetarli miqdor yo'q. Qolgan: {product.quantity}")
        amount = product.price * item.quantity
        profit = (product.price - product.cost_price) * item.quantity
        total_amount += amount
        total_profit += profit
        si = SaleItem(
            sale_id=sale.id,
            product_id=product.id,
            product_name=product.name,
            quantity=item.quantity,
            price=product.price,
            cost_price=product.cost_price,
            amount=amount,
            profit=profit
        )
        db.add(si)
        product.quantity -= item.quantity
    sale.total_amount = total_amount
    sale.total_profit = total_profit
    db.commit()
    db.refresh(sale)
    return sale


@router.get("", response_model=list[SaleResponse])
def list_sales(
    from_date: date | None = Query(None),
    to_date: date | None = Query(None),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    q = db.query(Sale).order_by(Sale.created_at.desc()).limit(limit)
    if from_date:
        q = q.filter(func.date(Sale.created_at) >= from_date)
    if to_date:
        q = q.filter(func.date(Sale.created_at) <= to_date)
    return q.all()


@router.get("/{id}", response_model=SaleResponse)
def get_sale(
    id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    s = db.query(Sale).filter(Sale.id == id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Sotuv topilmadi")
    return s
