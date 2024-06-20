import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings
from apscheduler.schedulers.background import BackgroundScheduler

from .routers import users, calculations, jobs, structures
from cluster import interaction_with_cluster

dotenv_path = os.getcwd()+"/.env"
load_dotenv(dotenv_path)

class Settings(BaseSettings):
    BASE_URL: str = os.environ.get("BASE_URL")

settings = Settings()

@asynccontextmanager
async def lifespan(_: FastAPI):
    scheduler = BackgroundScheduler()
    # TODO: Consider the need to dynamically adjust interval settings
    scheduler.add_job(interaction_with_cluster, 'interval', hours=2)
    scheduler.start()
    yield
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.environ.get("FE_URL")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(calculations.router)
app.include_router(jobs.router)
app.include_router(structures.router)

@app.get("/")
async def root():
    return 'hello world'
