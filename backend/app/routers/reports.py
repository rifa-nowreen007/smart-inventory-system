import csv, io
from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Product, Transaction
from . import get_current_user, require_manager

router = APIRouter(prefix="/api/reports", tags=["Reports"])

@router.get("/summary")
def summary(db: Session=Depends(get_db), _=Depends(get_current_user)):
    P = db.query(Product).all()
    T = db.query(Transaction).all()
    return {"total_products":len(P),"total_value":round(sum(p.stock*p.price for p in P),2),"low_stock":sum(1 for p in P if p.stock<=p.min_stock),"out_of_stock":sum(1 for p in P if p.stock==0),"total_sales":round(sum(t.total for t in T if t.type=="sale"),2),"total_purchases":round(sum(t.total for t in T if t.type=="purchase"),2),"tx_count":len(T)}

@router.get("/inventory/csv")
def export_csv(db: Session=Depends(get_db), _=Depends(require_manager)):
    P = db.query(Product).order_by(Product.name).all()
    out = io.StringIO(); w = csv.writer(out)
    w.writerow(["SKU","Name","Category","Supplier","Price","Stock","Min","Reorder","Value","Status"])
    for p in P:
        s = "Out" if p.stock==0 else ("Low" if p.stock<=p.min_stock else "OK")
        w.writerow([p.sku,p.name,p.category,p.supplier,p.price,p.stock,p.min_stock,p.reorder_qty,round(p.stock*p.price,2),s])
    return Response(content=out.getvalue(), media_type="text/csv", headers={"Content-Disposition":'attachment; filename="inventory.csv"'})
