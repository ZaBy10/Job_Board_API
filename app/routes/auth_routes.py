from fastapi import APIRouter, HTTPException
from sqlmodel import select  
from models.users import User_SignUp, Users , Role
from database import SessionDep
from security.password import verify_password,get_password_hash
from typing import Annotated
from fastapi.security import  OAuth2PasswordRequestForm
from fastapi import Depends, FastAPI, HTTPException, status
from security.jwt_auth import Token , authenticate_user , create_access_token , ACCESS_TOKEN_EXPIRE_MINUTES,get_current_user
from datetime import datetime, timedelta, timezone
from fastapi import Form


auth_router = APIRouter(
    prefix='/auth',
    tags=['Authorization']
)

# routes/auth_routes.py
from fastapi import Form  # Add this import

@auth_router.post("/signup", response_model=dict)
async def create_user(
    session: SessionDep,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: Role = Form(...)
    
):
    # Existing validation logic
    if session.exec(select(Users).where(Users.username == username)).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )

    if session.exec(select(Users).where(Users.email == email)).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists"
        )

    new_user = Users(
        username=username,
        email=email,
        password=get_password_hash(password),
        role=role
    )
    
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    return {"message": f"Successfully created user: {new_user.username}"}

@auth_router.post("/login", response_model=Token)
async def user_login(
    session: SessionDep,
    username: str = Form(...),
    password: str = Form(...)
    
):
    # Existing authentication logic
    user = authenticate_user(username, password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}



@auth_router.get("/")
def protected(current_user: Annotated[Users, Depends(get_current_user)],):
    return {'message':"welcome to my protected route!!!"}