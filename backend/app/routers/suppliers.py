from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..schemas import SupplierCreate, SupplierOut
from ..models import Supplier
from . import get_current_user, require_manager

router = APIRouter(prefix="/api/suppliers", tags=["Suppliers"])

@router.get("/", response_model=List[SupplierOut])
def list_suppliers(db: Session=Depends(get_db), _=Depends(get_current_user)):
    return db.query(Supplier).order_by(Supplier.name).all()

@router.post("/", response_model=SupplierOut, status_code=201)
def create_supplier(data: SupplierCreate, db: Session=Depends(get_db), _=Depends(require_manager)):
    if db.query(Supplier).filter(Supplier.name == data.name).first():
        raise HTTPException(status_code=409, detail="Supplier already exists")
    s = Supplier(**data.model_dump()); db.add(s); db.commit(); db.refresh(s); return s

@router.put("/{sid}", response_model=SupplierOut)
def update_supplier(sid: int, data: SupplierCreate, db: Session=Depends(get_db), _=Depends(require_manager)):
    s = db.query(Supplier).filter(Supplier.id == sid).first()
    if not s: raise HTTPException(status_code=404, detail="Supplier not found")
    for k, v in data.model_dump().items(): setattr(s, k, v)
    db.commit(); db.refresh(s); return s

@router.delete("/{sid}", status_code=204)
def delete_supplier(sid: int, db: Session=Depends(get_db), _=Depends(require_manager)):
    s = db.query(Supplier).filter(Supplier.id == sid).first()
    if not s: raise HTTPException(status_code=404, detail="Supplier not found")
    db.delete(s); db.commit()
