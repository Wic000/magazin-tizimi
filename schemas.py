"""Pydantic sxemalari"""
from datetime import datetime
from pydantic import BaseModel


# Auth
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class LoginRequest(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str = ""
    role: str = "kassir"


# Mahsulot
class ProductBase(BaseModel):
    name: str
    price: float
    cost_price: float = 0
    quantity: int = 0
    unit: str = "dona"


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = None
    price: float | None = None
    cost_price: float | None = None
    quantity: int | None = None
    unit: str | None = None
    is_active: bool | None = None


class ProductResponse(ProductBase):
    id: int
    is_active: bool
    created_at: datetime
    class Config:
        from_attributes = True


# Sotuv
class SaleItemCreate(BaseModel):
    product_id: int
    quantity: int


class SaleCreate(BaseModel):
    items: list[SaleItemCreate]


class SaleItemResponse(BaseModel):
    product_name: str
    quantity: int
    price: float
    amount: float
    profit: float
    class Config:
        from_attributes = True


class SaleResponse(BaseModel):
    id: int
    total_amount: float
    total_profit: float
    created_at: datetime
    user_id: int
    items: list[SaleItemResponse] = []
    class Config:
        from_attributes = True


# Hisobot
class ReportSummary(BaseModel):
    total_products: int
    total_quantity: int
    total_sold: int
    total_profit: float
    today_profit: float
    today_sales_count: int
