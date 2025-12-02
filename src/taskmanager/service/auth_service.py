from datetime import datetime, timedelta, timezone
from jose import jwt
from sqlalchemy.orm import Session
from src.taskmanager.model import User
from src.taskmanager.core import settings

def create_user_service(create_user_request, db : Session, bcrypt_contex):
    new_user = Use(
        email=create_user_request.email,
        hashed_password=bcrypt_contex.hash(create_user_request.password)
                    )
    db.add(new_user)
    db.commit()

def authenticate_user_service(email : str, password : str, db : Session, bcrypt_context):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return False
    if not bcrypt_context.verify(password,user.hashed_password):
        return False
    return user

def create_access_token_service(email :str, user_id :int, expire_delta : timedelta):
    expires = datetime.now(timezone.utc) + expire_delta
    encode = {"sub":email, "id":user_id, "exp":expires}
    return jwt.encode(encode, settings["AUTH_SECRET_KEY"], algorithm=settings["AUTH_ALGORITHM"])

