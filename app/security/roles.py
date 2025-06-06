from models.users import Users
from database import SessionDep 
from fastapi import HTTPException
from models.applications import Applications
from sqlmodel import select
from models.jobs import Jobs


def check_recruiter(user : Users):
    if user.role!='recruiter':
        raise HTTPException(status_code=401, detail="You are not a recruitor to perform the action!!!")
    else:
        return True
    
    
def check_job_seeker(user : Users):
    if user.role!='candidate':
        raise HTTPException(status_code=401,detail="You are not a candidate to perform the action!!!")
    else:
        return True
    
def check_valid_recruiter(user: Users , id : int , session : SessionDep):
    application = session.exec(select(Applications).where(Applications.id==id).join(Jobs)).first()
    if application.job.recruiter_id==user.id: # type: ignore
        return True
    else:
        raise HTTPException(status_code=401, detail="You cannot change status of other recruiter's application!!!")