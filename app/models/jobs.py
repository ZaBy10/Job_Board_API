from typing import List, Optional,TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from enum import Enum
from models.applications import Status
from sqlalchemy.orm import relationship

if TYPE_CHECKING:
    from models.users import Users
    from models.applications import Applications

class Jobs(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=100)
    company_name: str = Field(max_length=100)
    description: str
    salary: float
    location: str = Field(max_length=100)
    recruiter_id: int = Field(foreign_key="users.id")
    
    recruiter: "Users" = Relationship(back_populates="jobs")
    applications: List["Applications"] = Relationship(back_populates="job",sa_relationship=relationship(
            "Applications", 
            cascade="all, delete-orphan",
            passive_deletes=True
        ))

class Create_Job(SQLModel):
    title: str = Field(max_length=100)
    company_name: str = Field(max_length=100)
    description: str
    salary: float
    location: str = Field(max_length=100)
    
class My_Jobs(SQLModel):
    application_id : int
    title : str
    company_name : str
    applied_at : datetime
    status : Status


class My_Applications(SQLModel):
    application_id : int
    title : str
    company_name : str
    applied_at : datetime
    status : Status
    applicant_id : int