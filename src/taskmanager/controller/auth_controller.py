from typing import Annotated
from fastapi import APIRouter, Depends, Response, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import timedelta

from src.taskmanager.service import(
    create_user_service,
    authenticate_user_service,
    create_access_token_service
)
from src.taskmanager.core import db_dependency, bcrypt_contex

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

class UserCreateRequest(BaseModel):
    email: str
    password : str

class Token(BaseModel):
    auth_token: str
    token_type : str

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(create_user_request : UserCreateRequest, db : db_dependency):
    create_user_service(create_user_request, db, bcrypt_contex)
    return {"response": "User Created"}

@router.post("/token", response_model=Token)
async def login(
    form_data : Annotated[OAuth2PasswordRequestForm, Depends()],
    db : db_dependency,
    response : Response
):
    user = authenticate_user_service(form_data.username, form_data.password, db, bcrypt_contex)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate user"
        )
    token = create_access_token_service(user.email,user.id, timedelta(minutes=60))

    response.set_cookie(
        key="jwt",
        value=token,
        httponly=True,
        max_age=3600,
        path="/",
        samesite="strict",
        secure=False
    )
    return {"auth_token" : token, "token_type" : "bearer"}

@router.post("/logout")
async def logout(response : Response):
    response.set_cookie(
        key="jwt",
        value="",
        httponly=True,
        max_age=0,
        path="/",
        samesite="strict",
        secure=False
    )
    return {"message": "Logged out successfully"}
