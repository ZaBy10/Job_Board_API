from fastapi import APIRouter , Depends,HTTPException , Query , status
from models.jobs import Create_Job , Jobs , My_Jobs,My_Applications
from database import SessionDep
from security.jwt_auth import get_current_user
from typing import Annotated
from models.users import Users
from security.roles import check_recruiter , check_job_seeker , check_valid_recruiter
from sqlmodel import select , func
from models.applications import Application_Create, Application_Out , Applications , StatusUpdate,Status
from fastapi import Query

app_router = APIRouter(
    prefix="/applications",
    tags=["Applications"]
)

@app_router.post("/Create_Jobs", response_model=Jobs)
async def create_jobs(current_user: Annotated[Users, Depends(get_current_user)],job : Create_Job , session : SessionDep ):
    check_recruiter(current_user)
    if current_user.id is None:
         raise HTTPException(
            status_code=401,
            detail="Invalid user credentials"
         )
    user_id = current_user.id
    new_job = Jobs(**job.model_dump(), recruiter_id=user_id)
    session.add(new_job)
    session.commit()
    session.refresh(new_job)
    return new_job
    
    
@app_router.get("/ListALlJobs", response_model=list[Jobs])
async def list_jobs(current_user: Annotated[Users, Depends(get_current_user)],
    session: SessionDep,  # Database session dependency

):
    return session.exec(select(Jobs)).all()



@app_router.post("/apply", response_model=Application_Out)
async def apply_to_job(  
    application_data: Application_Create,  
    session: SessionDep,
    current_user: Annotated[Users, Depends(get_current_user)]
):
    check_job_seeker(current_user)
    
    # Validate job exists
    job = session.get(Jobs, application_data.job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Prevent duplicate applications
    existing = session.exec(
        select(Applications).where(
            Applications.job_id == application_data.job_id,
            Applications.applicant_id == current_user.id
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Already applied to this job"
        )
    
    new_application = Applications(
        **application_data.model_dump(),
        applicant_id=current_user.id,
    )
    
    session.add(new_application)
    session.commit()
    session.refresh(new_application)
    return new_application
    

@app_router.get("/ListMyJobs")
async def listmyjobs(current_user: Annotated[Users, Depends(get_current_user)] , session : SessionDep):
    check_job_seeker(current_user)
    my_application = session.exec(select(Applications).where(Applications.applicant_id==current_user.id).join(Jobs)).all()
    if not my_application:
        return {'message' : 'You have not applied to any jobs yet!!'}
    my_jobs = []
    for app in my_application:
        if app.status!=None and app.id!=None:
            my_job = My_Jobs(application_id=app.id,title=app.job.title,
                            company_name=app.job.company_name,applied_at=app.applied_at,
                            status=app.status)
            my_jobs.append(my_job)
    return my_jobs

@app_router.put("/UpdateStatus")
async def updateStatus(update : StatusUpdate , current_user: Annotated[Users, Depends(get_current_user)] , session : SessionDep ):
    check_recruiter(current_user)
    check_valid_recruiter(current_user,update.application_id,session)
    application = session.exec(select(Applications).where(Applications.id == update.application_id)).first()
    application.status = update.status # type: ignore
    session.commit()
    session.refresh(application)
    return application

@app_router.get("/recruiter",response_model=list[Applications])
async def listmyapplications(current_user: Annotated[Users, Depends(get_current_user)] , 
                             session : SessionDep,
                             status: Status | None = Query(None)):
    check_recruiter(current_user)
    base_query = (
        select(Applications)
        .join(Jobs)
        .where(Jobs.recruiter_id == current_user.id)
    )
    
    if status:
        base_query = base_query.where(Applications.status == status)
    
    applications = session.exec(base_query).all()
    
    return applications
    
    
@app_router.get("/jobs/search")
async def search_jobs(
    session: SessionDep,
    title: str = Query(None),
    location: str = Query(None),
    min_salary: float = Query(None, ge=0)
):
    query = select(Jobs)
    if title:
        query = query.where(func.lower(Jobs.title).contains(func.lower(title)))
    if location:
        query = query.where(Jobs.location == location)
    if min_salary:
        query = query.where(Jobs.salary >= min_salary)
    
    return session.exec(query).all()

@app_router.delete("/jobs/delete" , response_model= dict)
async def deleteJob(session :SessionDep , current_user: Annotated[Users, Depends(get_current_user)],jobId : int):
    check_recruiter(current_user)
    job = session.exec(select(Jobs).where(Jobs.id==jobId)).first()
    if not job:
        raise HTTPException(status_code=404 , detail = "Job not found!!")
    if job.recruiter_id!= current_user.id:# type: ignore
        raise HTTPException(status_code=401, detail="You cannot delete job posted by other recruitors!!!")
    session.delete(job)
    session.commit()
    
    return {'message': "Succesfully deleted the job"}

@app_router.delete("/applications/delete" , response_model= dict)
async def deleteApplications(session : SessionDep ,current_user: Annotated[Users, Depends(get_current_user)],AppId : int ):
    check_job_seeker(current_user)
    application = session.exec(select(Applications).where(Applications.id==AppId)).first()
    if not application:
        raise HTTPException(status_code=404 , detail="Application not found!!")
    if application.applicant_id!=current_user.id:
        raise HTTPException(status_code=401 , detail="Invalid Operation!! Cannot delete Other's Application")
    session.delete(application)
    session.commit()
    
    return {'message':'Successfully deleted the application'}