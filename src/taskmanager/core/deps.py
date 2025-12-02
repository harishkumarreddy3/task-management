from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, Request
from passlib.context import CryptContext
from jose import jwt, JWTError
from src.taskmanager.database import SessionLocal
from src.taskmanager.core import settings

# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

# Bcrypt password context
bcrypt_contex = CryptContext(schemes=["bcrypt"], deprecated = "auto")

# Get current user from JWT in cookies
async def get_current_user(request : Request):
    token = request.cookies.get("jwt")
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token not found in cookies"
        )
    
    try:
        payload = jwt.decod(token, settings["AUTH_SECRET_KEY"], algorithms=[settings["AUTH_ALGORITHM"]])
        email = payload.get("sub")
        user_id = payload.get("id")
        if email is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        return {"email": email, "id": user_id}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
# Final dependency alias
user_dependency = Annotated[dict, Depends(get_current_user)]