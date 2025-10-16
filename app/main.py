from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routers.department import department_router
from app.database import database


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(
    title="Data Migration API",
    description="REST API for migrating historical employee data from CSV to SQL database",
    lifespan=lifespan,
    version="1.0.0",
)

app.include_router(department_router, prefix="/api/v1")
