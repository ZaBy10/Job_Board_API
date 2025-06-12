# Updated main.py
from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from database import create_db_and_tables, SessionDep
from routes.auth_routes import auth_router 
from routes.applications_routes import app_router
from routes.profile_routes import prof_router
from models.users import Users
from models.applications import Applications
from models.jobs import Jobs
from security.jwt_auth import get_current_user
from sqlmodel import select

app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Include your existing routers
app.include_router(auth_router)
app.include_router(app_router)
app.include_router(prof_router)
