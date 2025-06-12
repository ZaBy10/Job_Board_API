from fastapi import FastAPI
from database import create_db_and_tables
from routes.auth_routes import auth_router 
from routes.applications_routes import app_router
from routes.profile_routes import prof_router


app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Include your existing routers
app.include_router(auth_router)
app.include_router(app_router)
app.include_router(prof_router)
