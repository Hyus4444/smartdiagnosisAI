from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse


router = APIRouter(prefix="/signin", tags=["Users"])

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email ya registrado"
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
    

