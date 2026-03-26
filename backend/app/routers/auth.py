from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import LoginIn, TokenOut, UserOut, UserCreate
from ..services import authenticate, create_token, hash_password, make_avatar
from ..models import User
from . import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/login", response_model=TokenOut)
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = authenticate(db, data.email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_token({"sub": str(user.id), "role": user.role})
    return TokenOut(access_token=token, user_id=user.id, role=user.role, name=user.name, avatar=user.avatar)

@router.get("/me", response_model=UserOut)
def me(current=Depends(get_current_user)):
    return current

@router.post("/register", response_model=TokenOut, status_code=201)
def register(data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(name=data.name, email=data.email, hashed_pw=hash_password(data.password),
                role=data.role, dept=data.dept, avatar=make_avatar(data.name))
    db.add(user); db.commit(); db.refresh(user)
    token = create_token({"sub": str(user.id), "role": user.role})
    return TokenOut(access_token=token, user_id=user.id, role=user.role, name=user.name, avatar=user.avatar)
