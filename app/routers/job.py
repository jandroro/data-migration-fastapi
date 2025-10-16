import io
import pandas as pd
from fastapi import APIRouter, HTTPException, Depends, Query, Response, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import List
from app.database import get_db
from app.models.database_models import Job as DBJob
from app.models.pydantic_models import (
    Job,
    JobCreate,
    JobUpdate,
    JobWithEmployees,
    UploadResponse,
    BatchResponse,
)

router = APIRouter(
    prefix="/api/v1/jobs",
    tags=["jobs"],
)


@router.get("/", response_model=List[Job])
async def get_all_jobs(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of records to return"
    ),
    db: Session = Depends(get_db),
):
    jobs = db.query(DBJob).offset(skip).limit(limit).all()
    return jobs


@router.get("/{job_id}", response_model=JobWithEmployees)
async def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(DBJob).filter(DBJob.id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job


@router.post("/", response_model=Job, status_code=201)
async def create_job(
    job: JobCreate,
    db: Session = Depends(get_db),
):
    try:
        # Check if job name already exists
        existing = db.query(DBJob).filter(DBJob.job == job.job).first()

        if existing:
            raise HTTPException(status_code=400, detail="Job name already exists")

        db_job = DBJob(**job.model_dump())
        db.add(db_job)
        db.commit()
        db.refresh(db_job)
        return db_job
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Database constraint violation")
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred")


@router.put("/{job_id}", response_model=Job)
async def update_job(
    job_id: int,
    job: JobUpdate,
    db: Session = Depends(get_db),
):
    try:
        db_job = db.query(DBJob).filter(DBJob.id == job_id).first()

        if not db_job:
            raise HTTPException(status_code=404, detail="Job not found")

        # Check name uniqueness if name is being updated
        if job.job and job.job != db_job.job:
            existing = db.query(DBJob).filter(DBJob.job == job.job).first()
            if existing:
                raise HTTPException(status_code=400, detail="Job name already exists")

        # Update only provided fields
        update_data = job.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_job, field, value)

        db.commit()
        db.refresh(db_job)
        return db_job
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Database constraint violation")
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred")


@router.delete("/{job_id}", status_code=204)
async def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
):
    try:
        db_job = db.query(DBJob).filter(DBJob.id == job_id).first()

        if not db_job:
            raise HTTPException(status_code=404, detail="Job not found")

        db.delete(db_job)
        db.commit()
        return Response(status_code=204)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Database constraint violation")
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred")


@router.post("/upload", response_model=UploadResponse)
async def upload_jobs_csv(
    file: UploadFile = File(...),
    db: Session = Depends(
        get_db,
    ),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode("utf-8")), header=None)
        df.columns = ["id", "job"]

        # Validate data
        if df.isnull().any().any():
            raise HTTPException(status_code=400, detail="CSV contains null values")

        records_inserted = 0
        records_updated = 0

        for _, row in df.iterrows():
            existing = db.query(DBJob).filter(DBJob.id == int(row["id"])).first()

            if existing:
                existing.job = row["job"]
                records_updated += 1
            else:
                new_job = DBJob(id=int(row["id"]), job=row["job"])
                db.add(new_job)
                records_inserted += 1

        db.commit()

        return UploadResponse(
            message="Jobs uploaded successfully",
            records_inserted=records_inserted,
            records_updated=records_updated,
        )
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="CSV file is empty")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@router.post("/upload/batch", response_model=BatchResponse)
def batch_insert_jobs(jobs: List[Job], db: Session = Depends(get_db)):
    if len(jobs) < 1 or len(jobs) > 1000:
        raise HTTPException(
            status_code=400, detail="Batch size must be between 1 and 1000 records"
        )

    try:
        records_inserted = 0
        bulk_job = []

        for job_data in jobs:
            job = DBJob(**job_data.model_dump())
            bulk_job.append(job)
            records_inserted += 1

        db.bulk_save_objects(bulk_job)
        db.commit()

        return BatchResponse(
            message="Batch insert successful", records_processed=records_inserted
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
