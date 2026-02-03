import re
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse


router = APIRouter(prefix="/auth", tags=["Users"])
PASSWORD_REGEX = re.compile(r"^(?=.*[0-9!@#$%^&*(),.?\":{}|<>]).{7,}$")

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email ya registrado"
        )
    if not "@" in user_in.email:
        raise HTTPException(
            status_code=400,
            detail="Formato de email inválido"
        )
    if not PASSWORD_REGEX.match(user_in.password):
        raise HTTPException(
            status_code=400,
            detail="Contraseña invalida",
    )
    user = User(
    email=user_in.email,
    password_hash = get_password_hash(user_in.password),
    full_name=user_in.full_name
)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

    

