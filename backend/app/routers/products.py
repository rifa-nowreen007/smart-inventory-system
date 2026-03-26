from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..schemas import ProductCreate, ProductUpdate, ProductOut, StockAdjust, TransactionOut
from ..models import Product, Transaction
from . import get_current_user, require_admin

router = APIRouter(prefix="/api/products", tags=["Products"])

@router.get("/", response_model=List[ProductOut])
def list_products(q: Optional[str]=Query(None), category: Optional[str]=Query(None), db: Session=Depends(get_db), _=Depends(get_current_user)):
    query = db.query(Product)
    if q: query = query.filter(Product.name.ilike(f"%{q}%") | Product.sku.ilike(f"%{q}%"))
    if category: query = query.filter(Product.category == category)
    return query.order_by(Product.name).all()

@router.get("/low-stock", response_model=List[ProductOut])
def low_stock(db: Session=Depends(get_db), _=Depends(get_current_user)):
    return db.query(Product).filter(Product.stock <= Product.min_stock).all()

@router.post("/", response_model=ProductOut, status_code=201)
def create_product(data: ProductCreate, db: Session=Depends(get_db), _=Depends(require_admin)):
    if db.query(Product).filter(Product.sku == data.sku).first():
        raise HTTPException(status_code=409, detail=f"SKU '{data.sku}' already exists")
    p = Product(**data.model_dump()); db.add(p); db.commit(); db.refresh(p); return p

@router.put("/{pid}", response_model=ProductOut)
def update_product(pid: int, data: ProductUpdate, db: Session=Depends(get_db), _=Depends(require_admin)):
    p = db.query(Product).filter(Product.id == pid).first()
    if not p: raise HTTPException(status_code=404, detail="Product not found")
    for k, v in data.model_dump(exclude_none=True).items(): setattr(p, k, v)
    db.commit(); db.refresh(p); return p

@router.delete("/{pid}", status_code=204)
def delete_product(pid: int, db: Session=Depends(get_db), _=Depends(require_admin)):
    p = db.query(Product).filter(Product.id == pid).first()
    if not p: raise HTTPException(status_code=404, detail="Product not found")
    db.delete(p); db.commit()

@router.post("/{pid}/stock", response_model=TransactionOut)
def adjust_stock(pid: int, data: StockAdjust, db: Session=Depends(get_db), user=Depends(get_current_user)):
    p = db.query(Product).filter(Product.id == pid).first()
    if not p: raise HTTPException(status_code=404, detail="Product not found")
    if data.type == "purchase": p.stock += data.qty
    elif data.type == "sale":
        if data.qty > p.stock: raise HTTPException(status_code=400, detail=f"Only {p.stock} in stock")
        p.stock -= data.qty
    else: raise HTTPException(status_code=400, detail="type must be purchase or sale")
    tx = Transaction(product_id=p.id, user_id=user.id, type=data.type, qty=data.qty, unit_price=p.price, total=round(data.qty*p.price,2), note=data.note)
    db.add(tx); db.commit(); db.refresh(tx); db.refresh(p)
    return TransactionOut(id=tx.id, product_id=tx.product_id, user_id=tx.user_id, type=tx.type, qty=tx.qty, unit_price=tx.unit_price, total=tx.total, note=tx.note or "", created_at=tx.created_at, product_name=p.name, product_sku=p.sku, user_name=user.name)
