from fastapi import APIRouter , Depends,HTTPException , status
from database import SessionDep
from security.jwt_auth import get_current_user
from models.users import Users , User_Details
from typing import Annotated
from sqlmodel import Field , select



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
        