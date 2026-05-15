##Documento transversal para declarar las dependencias comunes utilizadas en los endpoints, como la autenticación de usuarios y la gestión de sesiones de base de datos.
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from typing import cast
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User

load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

SECRET_KEY = cast(str, os.getenv("SECRET_KEY"))
ALGORITHM = "HS256"

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
