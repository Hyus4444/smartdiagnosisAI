from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import cast
from app.core.database import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, Token
from app.core.security import verify_password, create_access_token
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=Token)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token}

@router.get("/me")
def read_me(current_user = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name
    }
