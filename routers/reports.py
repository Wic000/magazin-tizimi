"""Hisobotlar API"""
from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import Product, Sale, SaleItem, User
from auth import get_current_user, require_admin

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/summary")
def report_summary(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    today = date.today()
    # Jami mahsulotlar
    products = db.query(Product).filter(Product.is_active == True).all()
    total_quantity = sum(p.quantity for p in products)
    total_products = len(products)
    # Jami sotilgan va foyda
    sold = db.query(
        func.coalesce(func.sum(SaleItem.quantity), 0).label("qty"),
        func.coalesce(func.sum(SaleItem.profit), 0).label("profit")
    ).first()
    total_sold = int(sold.qty) if sold else 0
    total_profit = float(sold.profit) if sold else 0.0
    # Bugungi
    today_sales = db.query(Sale).filter(func.date(Sale.created_at) == today).all()
    today_profit = sum(s.total_profit for s in today_sales)
    today_count = len(today_sales)
    return {
        "total_products": total_products,
        "total_quantity": total_quantity,
        "total_sold": total_sold,
        "total_profit": round(total_profit, 2),
        "today_profit": round(today_profit, 2),
        "today_sales_count": today_count
    }


@router.get("/profit-by-date")
def profit_by_date(
    from_date: date = Query(...),
    to_date: date = Query(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    rows = db.query(
        func.date(Sale.created_at).label("sana"),
        func.sum(Sale.total_amount).label("summa"),
        func.sum(Sale.total_profit).label("foyda")
    ).filter(
        func.date(Sale.created_at) >= from_date,
        func.date(Sale.created_at) <= to_date
    ).group_by(func.date(Sale.created_at)).order_by(func.date(Sale.created_at)).all()
    return [
        {"sana": str(r.sana), "summa": float(r.summa or 0), "foyda": float(r.foyda or 0)}
        for r in rows
    ]


@router.get("/top-products")
def top_products(
    from_date: date | None = Query(None),
    to_date: date | None = Query(None),
    limit: int = Query(10, le=50),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    q = db.query(
        SaleItem.product_name,
        func.sum(SaleItem.quantity).label("qty"),
        func.sum(SaleItem.amount).label("summa"),
        func.sum(SaleItem.profit).label("foyda")
    ).join(Sale).group_by(SaleItem.product_name)
    if from_date:
        q = q.filter(func.date(Sale.created_at) >= from_date)
    if to_date:
        q = q.filter(func.date(Sale.created_at) <= to_date)
    rows = q.order_by(func.sum(SaleItem.quantity).desc()).limit(limit).all()
    return [
        {
            "product_name": r.product_name,
            "quantity": int(r.qty),
            "amount": float(r.summa or 0),
            "profit": float(r.foyda or 0)
        }
        for r in rows
    ]
