from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models import User, Product, Supplier, Order, Transaction
from ..schemas import (LoginRequest, Token, UserCreate, UserUpdate, UserOut,
                       ProductCreate, ProductUpdate, ProductOut, StockAdjust,
                       SupplierCreate, SupplierOut, OrderCreate, OrderUpdate, OrderOut,
                       TransactionOut)
from ..services import hash_password, create_token, authenticate
from ..dependencies import get_current_user, require_admin, require_manager
import csv, io
from datetime import datetime


# ═══════════════ AUTH ═══════════════
auth_router = APIRouter(prefix="/api/auth", tags=["Auth"])

@auth_router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    token = create_token({"sub": str(user.id), "role": user.role})
    return Token(access_token=token, user_id=user.id, role=user.role,
                 name=user.name, avatar=user.avatar, dept=user.dept)

@auth_router.get("/me", response_model=UserOut)
def me(u: User = Depends(get_current_user)):
    return u


# ═══════════════ USERS ═══════════════
users_router = APIRouter(prefix="/api/users", tags=["Users"])

@users_router.get("/", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db), _=Depends(require_admin)):
    return db.query(User).order_by(User.id).all()

@users_router.post("/", response_model=UserOut, status_code=201)
def create_user(p: UserCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    if db.query(User).filter(User.email == p.email).first():
        raise HTTPException(409, "Email already registered")
    av = "".join(w[0] for w in p.name.split())[:2].upper()
    u = User(name=p.name, email=p.email, hashed_pw=hash_password(p.password),
             role=p.role, dept=p.dept, avatar=av)
    db.add(u); db.commit(); db.refresh(u)
    return u

@users_router.put("/{uid}", response_model=UserOut)
def update_user(uid: int, p: UserUpdate, db: Session = Depends(get_db), _=Depends(require_admin)):
    u = db.query(User).filter(User.id == uid).first()
    if not u: raise HTTPException(404, "User not found")
    for k, v in p.model_dump(exclude_none=True).items():
        if k == "password":
            u.hashed_pw = hash_password(v)
        else:
            setattr(u, k, v)
    db.commit(); db.refresh(u)
    return u

@users_router.delete("/{uid}", status_code=204)
def delete_user(uid: int, db: Session = Depends(get_db), me: User = Depends(require_admin)):
    if uid == me.id: raise HTTPException(400, "Cannot delete your own account")
    u = db.query(User).filter(User.id == uid).first()
    if not u: raise HTTPException(404, "Not found")
    db.delete(u); db.commit()


# ═══════════════ PRODUCTS ═══════════════
products_router = APIRouter(prefix="/api/products", tags=["Products"])

@products_router.get("/", response_model=List[ProductOut])
def list_products(category: Optional[str] = None, supplier: Optional[str] = None,
                  db: Session = Depends(get_db), _=Depends(get_current_user)):
    q = db.query(Product).filter(Product.status == "active")
    if category: q = q.filter(Product.category == category)
    if supplier:  q = q.filter(Product.supplier == supplier)
    return q.order_by(Product.name).all()

@products_router.get("/low-stock", response_model=List[ProductOut])
def low_stock(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Product).filter(Product.stock <= Product.min_stock, Product.status == "active").all()

@products_router.post("/", response_model=ProductOut, status_code=201)
def create_product(p: ProductCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    if db.query(Product).filter(Product.sku == p.sku).first():
        raise HTTPException(409, f"SKU '{p.sku}' already exists")
    prod = Product(**p.model_dump())
    db.add(prod); db.commit(); db.refresh(prod)
    return prod

@products_router.put("/{pid}", response_model=ProductOut)
def update_product(pid: int, p: ProductUpdate, db: Session = Depends(get_db), _=Depends(require_admin)):
    prod = db.query(Product).filter(Product.id == pid).first()
    if not prod: raise HTTPException(404, "Product not found")
    for k, v in p.model_dump(exclude_none=True).items():
        setattr(prod, k, v)
    db.commit(); db.refresh(prod)
    return prod

@products_router.delete("/{pid}", status_code=204)
def delete_product(pid: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    prod = db.query(Product).filter(Product.id == pid).first()
    if not prod: raise HTTPException(404, "Not found")
    db.delete(prod); db.commit()

@products_router.post("/{pid}/stock", response_model=TransactionOut)
def adjust_stock(pid: int, p: StockAdjust, db: Session = Depends(get_db),
                 me: User = Depends(get_current_user)):
    prod = db.query(Product).filter(Product.id == pid).first()
    if not prod: raise HTTPException(404, "Product not found")
    if p.tx_type == "purchase":
        prod.stock += p.qty
    elif p.tx_type == "sale":
        if p.qty > prod.stock:
            raise HTTPException(400, f"Insufficient stock: have {prod.stock}, need {p.qty}")
        prod.stock -= p.qty
    else:
        raise HTTPException(400, "tx_type must be 'purchase' or 'sale'")
    tx = Transaction(product_id=prod.id, user_id=me.id, tx_type=p.tx_type,
                     qty=p.qty, unit_price=prod.unit_price,
                     total=round(p.qty * prod.unit_price, 2), note=p.note)
    db.add(tx); db.commit(); db.refresh(tx); db.refresh(prod)
    return TransactionOut(id=tx.id, product_id=tx.product_id, user_id=tx.user_id,
                          tx_type=tx.tx_type, qty=tx.qty, unit_price=tx.unit_price,
                          total=tx.total, note=tx.note, created_at=tx.created_at,
                          product_name=prod.name, product_sku=prod.sku, user_name=me.name)


# ═══════════════ SUPPLIERS ═══════════════
suppliers_router = APIRouter(prefix="/api/suppliers", tags=["Suppliers"])

@suppliers_router.get("/", response_model=List[SupplierOut])
def list_suppliers(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Supplier).order_by(Supplier.name).all()

@suppliers_router.post("/", response_model=SupplierOut, status_code=201)
def create_supplier(p: SupplierCreate, db: Session = Depends(get_db), _=Depends(require_manager)):
    s = Supplier(**p.model_dump())
    db.add(s); db.commit(); db.refresh(s)
    return s

@suppliers_router.put("/{sid}", response_model=SupplierOut)
def update_supplier(sid: int, p: SupplierCreate, db: Session = Depends(get_db), _=Depends(require_manager)):
    s = db.query(Supplier).filter(Supplier.id == sid).first()
    if not s: raise HTTPException(404, "Not found")
    for k, v in p.model_dump().items(): setattr(s, k, v)
    db.commit(); db.refresh(s)
    return s

@suppliers_router.delete("/{sid}", status_code=204)
def delete_supplier(sid: int, db: Session = Depends(get_db), _=Depends(require_manager)):
    s = db.query(Supplier).filter(Supplier.id == sid).first()
    if not s: raise HTTPException(404, "Not found")
    db.delete(s); db.commit()


# ═══════════════ ORDERS ═══════════════
orders_router = APIRouter(prefix="/api/orders", tags=["Orders"])

@orders_router.get("/", response_model=List[OrderOut])
def list_orders(status: Optional[str] = None, db: Session = Depends(get_db),
                _=Depends(get_current_user)):
    q = db.query(Order)
    if status: q = q.filter(Order.status == status)
    return q.order_by(Order.id.desc()).all()

@orders_router.post("/", response_model=OrderOut, status_code=201)
def create_order(p: OrderCreate, db: Session = Depends(get_db), _=Depends(require_manager)):
    count = db.query(Order).count()
    ref   = f"ORD-{str(count + 1).zfill(3)}"
    o = Order(order_ref=ref, **p.model_dump())
    db.add(o); db.commit(); db.refresh(o)
    return o

@orders_router.put("/{oid}", response_model=OrderOut)
def update_order(oid: int, p: OrderUpdate, db: Session = Depends(get_db), _=Depends(require_manager)):
    o = db.query(Order).filter(Order.id == oid).first()
    if not o: raise HTTPException(404, "Not found")
    for k, v in p.model_dump(exclude_none=True).items(): setattr(o, k, v)
    db.commit(); db.refresh(o)
    return o

@orders_router.delete("/{oid}", status_code=204)
def delete_order(oid: int, db: Session = Depends(get_db), _=Depends(require_manager)):
    o = db.query(Order).filter(Order.id == oid).first()
    if not o: raise HTTPException(404, "Not found")
    db.delete(o); db.commit()


# ═══════════════ TRANSACTIONS ═══════════════
tx_router = APIRouter(prefix="/api/transactions", tags=["Transactions"])

@tx_router.get("/", response_model=List[TransactionOut])
def list_transactions(skip: int = 0, limit: int = 200,
                      db: Session = Depends(get_db), me: User = Depends(get_current_user)):
    q = db.query(Transaction)
    if me.role == "staff":
        q = q.filter(Transaction.user_id == me.id)
    txs = q.order_by(Transaction.id.desc()).offset(skip).limit(limit).all()
    result = []
    for t in txs:
        result.append(TransactionOut(
            id=t.id, product_id=t.product_id, user_id=t.user_id,
            tx_type=t.tx_type, qty=t.qty, unit_price=t.unit_price,
            total=t.total, note=t.note or "", created_at=t.created_at,
            product_name=t.product.name if t.product else None,
            product_sku=t.product.sku  if t.product else None,
            user_name=t.user.name       if t.user    else None,
        ))
    return result


# ═══════════════ REPORTS ═══════════════
reports_router = APIRouter(prefix="/api/reports", tags=["Reports"])

@reports_router.get("/summary")
def summary(db: Session = Depends(get_db), _=Depends(get_current_user)):
    prods = db.query(Product).filter(Product.status == "active").all()
    txs   = db.query(Transaction).all()
    return {
        "total_products":  len(prods),
        "total_value":     round(sum(p.stock * p.unit_price for p in prods), 2),
        "low_stock_count": sum(1 for p in prods if p.stock <= p.min_stock),
        "out_of_stock":    sum(1 for p in prods if p.stock <= 0),
        "total_sales":     round(sum(t.total for t in txs if t.tx_type == "sale"), 2),
        "total_purchases": round(sum(t.total for t in txs if t.tx_type == "purchase"), 2),
        "transaction_count": len(txs),
    }

@reports_router.get("/inventory/csv")
def inventory_csv(db: Session = Depends(get_db), _=Depends(require_manager)):
    prods  = db.query(Product).filter(Product.status == "active").order_by(Product.name).all()
    output = io.StringIO()
    w = csv.writer(output)
    w.writerow(["SKU","Name","Category","Supplier","Price","Stock","Min","Reorder","Value","Status"])
    for p in prods:
        s = "Out" if p.stock <= 0 else ("Low" if p.stock <= p.min_stock else "OK")
        w.writerow([p.sku, p.name, p.category, p.supplier, p.unit_price,
                    p.stock, p.min_stock, p.reorder_qty,
                    round(p.stock * p.unit_price, 2), s])
    fn = f"inventory_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    return Response(content=output.getvalue(), media_type="text/csv",
                    headers={"Content-Disposition": f'attachment; filename="{fn}"'})
