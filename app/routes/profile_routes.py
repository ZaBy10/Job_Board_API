from fastapi import APIRouter , Depends,HTTPException , status
from database import SessionDep
from security.jwt_auth import get_current_user
from models.users import Users , User_Details
from typing import Annotated
from sqlmodel import Field , select
import secrets
from security.password import get_password_hash
from datetime import datetime , timedelta

reset_tokens = {}  #For password Change


prof_router = APIRouter(
    prefix="/Profile",
    tags=["User_Profile"]
)

@prof_router.get("/details" , response_model= User_Details)
async def user_details(session : SessionDep ,current_user: Annotated[Users, Depends(get_current_user)] ):
    return current_user

@prof_router.put("/updateProfile")
async def profile_update(session : SessionDep , current_user : Annotated[Users,Depends(get_current_user)],
                         email : str = None,# type: ignore
                         username : str = None # type: ignore
                         ):
    if email:
        if current_user.email == email :
            raise HTTPException(status_code=404 , detail = "Cannot change into the same email")
    if username :
        if current_user.username == username :
            raise HTTPException(status_code=404 , detail = "Cannot change into the same username")
        
    if session.exec(select(Users).where(Users.email==email)).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT , detail="Email Already Exists!!!")
    if session.exec(select(Users).where(Users.username==username)).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT , detail="Username Already Exists!!!")
    
    if email:
        current_user.email = email
        session.add(current_user)
        session.commit()
        
    if username:
        current_user.username = username 
        session.add(current_user)
        session.commit()
        
    return {'message':'Successfully updated your Profile!!!'}


@prof_router.post("/request-password-reset")
async def request_password_reset(email: str, session: SessionDep):
    """Step 1: Request reset token (no authentication required)"""
    user = session.exec(select(Users).where(Users.email == email)).first()
    if not user:
        # Always return success to prevent email enumeration
        return {"message": "If your email exists, you'll receive reset instructions"}
    
    # Generate secure token with expiration
    token = secrets.token_urlsafe(32)
    reset_tokens[token] = {
        "user_id": user.id,
        "expires": datetime.utcnow() + timedelta(minutes=30)
    }
    
    print(f"\n🔑 Password reset token for {email}: {token}\n")
    
    return {"message": "Password reset instructions sent"}


        
@prof_router.post("/reset-password")
async def reset_password(
    session: SessionDep, 
    token: str, 
    password: str
):
    """Step 2: Reset password using token (no authentication required)"""
    token_data = reset_tokens.pop(token, None)
    
    # Validate token
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )
    
    if datetime.utcnow() > token_data["expires"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token has expired"
        )
    
    # Get user from token's user_id (not from current session)
    user = session.get(Users, token_data["user_id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters")
    # Update password
    user.password = get_password_hash(password)
    session.add(user)
    session.commit()
    
    return {"message": "Password updated successfully"}
    