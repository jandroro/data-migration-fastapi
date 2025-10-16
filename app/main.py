from fastapi import FastAPI
from app.routers import department, job, employee
from app.database import Base, engine


# Create database tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Data Migration API",
    description="REST API for migrating historical employee data from CSV to SQL database",
    version="1.0.0",
)

# Include routers
app.include_router(department.router)
app.include_router(job.router)
app.include_router(employee.router)
