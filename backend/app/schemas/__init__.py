from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# ── Auth ──────────────────────────────────────
class LoginRequest(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    role: str
    name: str
    avatar: str
    dept: str


# ── User ──────────────────────────────────────
class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str = "staff"
    dept: str = "General"

class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    dept: Optional[str] = None
    password: Optional[str] = None
    status: Optional[str] = None

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str
    dept: str
    avatar: str
    status: str
    created_at: datetime
    class Config:
        from_attributes = True


# ── Product ───────────────────────────────────
class ProductCreate(BaseModel):
    sku: str
    name: str
    category: str
    supplier: str = ""
    unit_price: float
    stock: int = 0
    min_stock: int = 10
    reorder_qty: int = 50

class ProductUpdate(BaseModel):
    sku: Optional[str] = None
    name: Optional[str] = None
    category: Optional[str] = None
    supplier: Optional[str] = None
    unit_price: Optional[float] = None
    stock: Optional[int] = None
    min_stock: Optional[int] = None
    reorder_qty: Optional[int] = None
    status: Optional[str] = None

class ProductOut(BaseModel):
    id: int
    sku: str
    name: str
    category: str
    supplier: str
    unit_price: float
    stock: int
    min_stock: int
    reorder_qty: int
    status: str
    created_at: datetime
    class Config:
        from_attributes = True

class StockAdjust(BaseModel):
    tx_type: str       # "purchase" | "sale"
    qty: int
    note: str = ""


# ── Supplier ──────────────────────────────────
class SupplierCreate(BaseModel):
    name: str
    category: str = ""
    contact: str = ""
    phone: str = ""
    status: str = "active"

class SupplierOut(BaseModel):
    id: int
    name: str
    category: str
    contact: str
    phone: str
    status: str
    class Config:
        from_attributes = True


# ── Order ─────────────────────────────────────
class OrderCreate(BaseModel):
    supplier: str
    items: int = 1
    total: float = 0.0
    status: str = "pending"
    note: str = ""
    order_date: str = ""

class OrderUpdate(BaseModel):
    supplier: Optional[str] = None
    items: Optional[int] = None
    total: Optional[float] = None
    status: Optional[str] = None
    note: Optional[str] = None
    order_date: Optional[str] = None

class OrderOut(BaseModel):
    id: int
    order_ref: str
    supplier: str
    items: int
    total: float
    status: str
    note: str
    order_date: str
    created_at: datetime
    class Config:
        from_attributes = True


# ── Transaction ───────────────────────────────
class TransactionOut(BaseModel):
    id: int
    product_id: int
    user_id: int
    tx_type: str
    qty: int
    unit_price: float
    total: float
    note: str
    created_at: datetime
    product_name: Optional[str] = None
    product_sku: Optional[str] = None
    user_name: Optional[str] = None
    class Config:
        from_attributes = True
