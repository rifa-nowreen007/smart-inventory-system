from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class User(Base):
    __tablename__ = "users"
    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String(120), nullable=False)
    email      = Column(String(255), unique=True, index=True, nullable=False)
    hashed_pw  = Column(String(255), nullable=False)
    role       = Column(String(20), default="staff")
    dept       = Column(String(80), default="General")
    avatar     = Column(String(5), default="?")
    status     = Column(String(20), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    transactions = relationship("Transaction", back_populates="user")


class Product(Base):
    __tablename__ = "products"
    id          = Column(Integer, primary_key=True, index=True)
    sku         = Column(String(30), unique=True, index=True, nullable=False)
    name        = Column(String(200), nullable=False, index=True)
    category    = Column(String(80), nullable=False)
    supplier    = Column(String(120), default="")
    unit_price  = Column(Float, nullable=False)
    stock       = Column(Integer, default=0)
    min_stock   = Column(Integer, default=10)
    reorder_qty = Column(Integer, default=50)
    status      = Column(String(20), default="active")
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    updated_at  = Column(DateTime(timezone=True), onupdate=func.now())
    transactions = relationship("Transaction", back_populates="product")


class Supplier(Base):
    __tablename__ = "suppliers"
    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String(120), nullable=False)
    category   = Column(String(80), default="")
    contact    = Column(String(255), default="")
    phone      = Column(String(50), default="")
    status     = Column(String(20), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Order(Base):
    __tablename__ = "orders"
    id          = Column(Integer, primary_key=True, index=True)
    order_ref   = Column(String(30), unique=True, index=True)
    supplier    = Column(String(120), nullable=False)
    items       = Column(Integer, default=1)
    total       = Column(Float, default=0.0)
    status      = Column(String(30), default="pending")
    note        = Column(Text, default="")
    order_date  = Column(String(20), default="")
    created_at  = Column(DateTime(timezone=True), server_default=func.now())


class Transaction(Base):
    __tablename__ = "transactions"
    id         = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    tx_type    = Column(String(20), nullable=False)   # purchase | sale
    qty        = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total      = Column(Float, nullable=False)
    note       = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    product    = relationship("Product", back_populates="transactions")
    user       = relationship("User", back_populates="transactions")
