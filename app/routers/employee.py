import io
import pandas as pd
from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from app.database import get_db
from app.models.database_models import Employee as DBEmployee
from app.models.database_models import Department as DBDepartment
from app.models.database_models import Job as DBJob
from app.models.pydantic_models import (
    Employee,
    UploadResponse,
    BatchResponse,
)

router = APIRouter(
    prefix="/api/v1/employees",
    tags=["employees"],
)


def parse_datetime_from_csv(dt_str: str) -> datetime:
    if not dt_str or dt_str.strip() == "":
        return None

    try:
        # Remove 'Z' and parse
        dt_str_cleaned = dt_str.replace("Z", "+00:00")
        return datetime.fromisoformat(dt_str_cleaned).replace(tzinfo=None)
    except Exception as e:
        return None


@router.get("/", response_model=List[Employee])
async def get_all_employees(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of records to return"
    ),
    db: Session = Depends(get_db),
):
    employees = db.query(DBEmployee).offset(skip).limit(limit).all()
    return employees


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
        df.columns = ["id", "name", "datetime", "department_id", "job_id"]

        records_inserted = 0
        records_updated = 0
        errors = []

        # Process in chunks for better memory management
        chunk_size = 1000
        for i in range(0, len(df), chunk_size):
            chunk = df.iloc[i : i + chunk_size]

            for idx, row in chunk.iterrows():
                try:
                    # Validate foreign keys
                    if pd.notna(row["department_id"]):
                        dept = (
                            db.query(DBDepartment)
                            .filter(DBDepartment.id == int(row["department_id"]))
                            .first()
                        )
                        if not dept:
                            errors.append(
                                f"Row {idx}: Department ID {int(row['department_id'])} not found"
                            )
                            continue

                    if pd.notna(row["job_id"]):
                        job = (
                            db.query(DBJob)
                            .filter(DBJob.id == int(row["job_id"]))
                            .first()
                        )
                        if not job:
                            errors.append(
                                f"Row {idx}: Job ID {int(row['job_id'])} not found"
                            )
                            continue

                    # Parse datetime from ISO format
                    hire_datetime = None
                    if pd.notna(row["datetime"]):
                        hire_datetime = parse_datetime_from_csv(str(row["datetime"]))

                    existing = (
                        db.query(DBEmployee)
                        .filter(DBEmployee.id == int(row["id"]))
                        .first()
                    )
                    if existing:
                        existing.name = row["name"] if pd.notna(row["name"]) else None
                        existing.datetime = (
                            hire_datetime if pd.notna(row["datetime"]) else None
                        )
                        existing.department_id = (
                            int(row["department_id"])
                            if pd.notna(row["department_id"])
                            else None
                        )
                        existing.job_id = (
                            int(row["job_id"]) if pd.notna(row["job_id"]) else None
                        )
                        records_updated += 1
                    else:
                        emp = DBEmployee(
                            id=int(row["id"]),
                            name=row["name"] if pd.notna(row["name"]) else None,
                            datetime=hire_datetime
                            if pd.notna(row["datetime"])
                            else None,
                            department_id=int(row["department_id"])
                            if pd.notna(row["department_id"])
                            else None,
                            job_id=int(row["job_id"])
                            if pd.notna(row["job_id"])
                            else None,
                        )

                        db.add(emp)
                        records_inserted += 1

                except Exception as e:
                    errors.append(f"Row {idx}: {str(e)}")

            db.commit()

        response = UploadResponse(
            message="Employees uploaded successfully"
            if not errors
            else "Employees uploaded with errors",
            records_inserted=records_inserted,
            records_updated=records_updated,
        )

        if errors:
            response.errors = errors[:10]  # Return first 10 errors

        return response

    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="CSV file is empty")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@router.post("/upload/batch", response_model=BatchResponse)
def batch_insert_employees(employees: List[Employee], db: Session = Depends(get_db)):
    if len(employees) < 1 or len(employees) > 1000:
        raise HTTPException(
            status_code=400,
            detail="Batch size must be between 1 and 1000 records",
        )

    try:
        # Validate foreign keys
        for emp in employees:
            if emp.department_id:
                dept = (
                    db.query(DBDepartment)
                    .filter(DBDepartment.id == emp.department_id)
                    .first()
                )
                if not dept:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Department ID {emp.department_id} not found",
                    )

            if emp.job_id:
                job = db.query(DBJob).filter(DBJob.id == emp.job_id).first()
                if not job:
                    raise HTTPException(
                        status_code=400, detail=f"Job ID {emp.job_id} not found"
                    )

        records_inserted = 0
        bulk_data = []
        for emp_data in employees:
            emp_dict = emp.model_dump()
            emp_dict["datetime"] = datetime.fromisoformat(
                emp_dict["datetime"].replace("Z", "+00:00")
            )
            emp = Employee(**emp_data.model_dump())
            bulk_data.append(emp)
            records_inserted += 1

        db.bulk_save_objects(bulk_data)
        db.commit()

        return BatchResponse(
            message="Batch insert successful", records_processed=records_inserted
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
