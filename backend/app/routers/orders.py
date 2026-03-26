from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..schemas import OrderCreate, OrderUpdate, OrderOut
from ..models import Order
from . import get_current_user, require_manager

router = APIRouter(prefix="/api/orders", tags=["Orders"])

@router.get("/", response_model=List[OrderOut])
def list_orders(status: Optional[str]=Query(None), db: Session=Depends(get_db), _=Depends(get_current_user)):
    q = db.query(Order)
    if status: q = q.filter(Order.status == status)
    return q.order_by(Order.created_at.desc()).all()

@router.post("/", response_model=OrderOut, status_code=201)
def create_order(data: OrderCreate, db: Session=Depends(get_db), _=Depends(require_manager)):
    count = db.query(Order).count()
    ref = f"ORD-{str(count+1).zfill(3)}"
    o = Order(order_ref=ref, **data.model_dump()); db.add(o); db.commit(); db.refresh(o); return o

@router.put("/{oid}", response_model=OrderOut)
def update_order(oid: int, data: OrderUpdate, db: Session=Depends(get_db), _=Depends(require_manager)):
    o = db.query(Order).filter(Order.id == oid).first()
    if not o: raise HTTPException(status_code=404, detail="Order not found")
    for k, v in data.model_dump(exclude_none=True).items(): setattr(o, k, v)
    db.commit(); db.refresh(o); return o

@router.delete("/{oid}", status_code=204)
def delete_order(oid: int, db: Session=Depends(get_db), _=Depends(require_manager)):
    o = db.query(Order).filter(Order.id == oid).first()
    if not o: raise HTTPException(status_code=404, detail="Order not found")
    db.delete(o); db.commit()
