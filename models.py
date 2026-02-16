"""SQLAlchemy modellari"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(String(20), default="kassir")  # admin, kassir
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    price = Column(Float, nullable=False)  # sotuv narxi
    cost_price = Column(Float, default=0)   # olish narxi (foyda hisoblash uchun)
    quantity = Column(Integer, default=0)
    unit = Column(String(20), default="dona")
    is_active = Column(Boolean, default=True)  # soft delete / arxivlash
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # sotuvlar
    sales = relationship("SaleItem", back_populates="product")


class Sale(Base):
    __tablename__ = "sales"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total_amount = Column(Float, default=0)
    total_profit = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    items = relationship("SaleItem", back_populates="sale")
    user = relationship("User")


class SaleItem(Base):
    __tablename__ = "sale_items"
    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    product_name = Column(String(200))
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    cost_price = Column(Float, default=0)
    amount = Column(Float, nullable=False)
    profit = Column(Float, default=0)
    sale = relationship("Sale", back_populates="items")
    product = relationship("Product", back_populates="sales")
