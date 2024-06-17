import os
import sys
from fastapi import Depends, FastAPI
from fastapi.logger import logger
from pydantic_settings import BaseSettings
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler

from .routers import users, calculations, jobs, structures
from cluster import interaction_with_cluster

import psutil

dotenv_path = os.getcwd()+"/.env"
load_dotenv(dotenv_path)

class Settings(BaseSettings):
    BASE_URL: str = os.environ.get("BASE_URL")

settings = Settings()


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.environ.get("FE_URL")],  # Replace with the URL of frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(calculations.router)
app.include_router(jobs.router)
app.include_router(structures.router)

scheduler = BackgroundScheduler()

@app.on_event("startup")
def start_scheduler():
    scheduler.add_job(interaction_with_cluster, 'interval', hours=2)
    scheduler.start()

@app.on_event("shutdown")
def shutdown_scheduler():
    scheduler.shutdown()

@app.get("/")
async def root():
    return 'hello world'
