from fastapi import FastAPI
from contextlib import asynccontextmanager
from . import models
from .database import engine
from .routers import projects, places

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield

app = FastAPI(
    title="Travel Planner API",
    description="API for managing travel projects and places.",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(projects.router)
app.include_router(places.router)

@app.get("/")
def root():
    return {"message": "Welcome to the Travel Planner API"}
