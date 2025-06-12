# users.py
from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from models.jobs import Jobs
    from models.applications import Applications

class Role(str, Enum):
    CANDIDATE = "candidate"
    RECRUITER = "recruiter"

class Users(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, max_length=50)
    email: str = Field(unique=True, max_length=100)
    password: str
    role: Role
    jobs: List["Jobs"] = Relationship(back_populates="recruiter")
    applications: List["Applications"] = Relationship(back_populates="applicant")

class User_SignUp(SQLModel):
    username: str = Field(max_length=50)  
    email: str = Field(max_length=100)    
    password: str 
    role: Role
    
class User_Details(SQLModel):
    id  : int 
    username : str 
    email : str
    role : Role