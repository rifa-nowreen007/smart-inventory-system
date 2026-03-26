from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..schemas import UserCreate, UserUpdate, UserOut
from ..services import hash_password, make_avatar
from ..models import User
from . import require_admin, get_current_user

router = APIRouter(prefix="/api/users", tags=["Users"])

@router.get("/", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db), _=Depends(require_admin)):
    return db.query(User).order_by(User.id).all()

@router.post("/", response_model=UserOut, status_code=201)
def create_user(data: UserCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(name=data.name, email=data.email, hashed_pw=hash_password(data.password),
                role=data.role, dept=data.dept, avatar=make_avatar(data.name))
    db.add(user); db.commit(); db.refresh(user); return user

@router.put("/{uid}", response_model=UserOut)
def update_user(uid: int, data: UserUpdate, db: Session = Depends(get_db), _=Depends(require_admin)):
    user = db.query(User).filter(User.id == uid).first()
    if not user: raise HTTPException(status_code=404, detail="User not found")
    if data.name:     user.name = data.name; user.avatar = make_avatar(data.name)
    if data.role:     user.role = data.role
    if data.dept:     user.dept = data.dept
    if data.password: user.hashed_pw = hash_password(data.password)
    db.commit(); db.refresh(user); return user

@router.delete("/{uid}", status_code=204)
def delete_user(uid: int, db: Session = Depends(get_db), me=Depends(require_admin)):
    if uid == me.id: raise HTTPException(status_code=400, detail="Cannot delete yourself")
    user = db.query(User).filter(User.id == uid).first()
    if not user: raise HTTPException(status_code=404, detail="User not found")
    if user.role == "admin": raise HTTPException(status_code=400, detail="Cannot delete admin")
    db.delete(user); db.commit()
