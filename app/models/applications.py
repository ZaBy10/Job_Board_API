from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional,TYPE_CHECKING
from enum import Enum
from datetime import datetime
if TYPE_CHECKING:
    from models.jobs import Jobs  
    from models.users import Users 
class Status(str, Enum):
    SELECTED = 'selected'
    REJECTED = 'rejected'
    UNDER_REVIEW = 'under_review'


class Applications(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    job_id: int = Field(foreign_key="jobs.id")
    applicant_id: Optional[int] = Field(foreign_key="users.id")
    resume_link: str
    status: Optional[Status] = Field(default="UNDER_REVIEW")
    applied_at: datetime = Field(default_factory=datetime.utcnow)
    # Relationship to Jobs and Users
    job: "Jobs" = Relationship(back_populates="applications")
    applicant: "Users" = Relationship(back_populates="applications")

class Application_Create(SQLModel):
    
    job_id : int 
    resume_link : str 
    
    
class Application_Out(SQLModel):
    
    id : int
    job_id : int 
    applicant_id :int 
    applied_at : datetime
    
class StatusUpdate(SQLModel):
    application_id : int 
    status : Status