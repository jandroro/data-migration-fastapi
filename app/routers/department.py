import csv
import io
import pandas as pd
from fastapi import APIRouter, HTTPException, Depends, Query, Response, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import List
from app.database import get_db
from app.models.database_models import Department as DBDepartment
from app.models.pydantic_models import (
    Department,
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentWithEmployees,
    UploadResponse,
    BatchResponse,
)

router = APIRouter(
    prefix="/api/v1/departments",
    tags=["departments"],
)


@router.get("/", response_model=List[Department])
async def get_all_departments(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of records to return"
    ),
    db: Session = Depends(get_db),
):
    departments = db.query(DBDepartment).offset(skip).limit(limit).all()
    return departments


@router.get("/{department_id}", response_model=DepartmentWithEmployees)
async def get_department(department_id: int, db: Session = Depends(get_db)):
    department = db.query(DBDepartment).filter(DBDepartment.id == department_id).first()

    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    return department


@router.post("/", response_model=Department, status_code=201)
async def create_department(
    department: DepartmentCreate,
    db: Session = Depends(get_db),
):
    try:
        # Check if department name already exists
        existing = (
            db.query(DBDepartment)
            .filter(DBDepartment.department == department.department)
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=400, detail="Department name already exists"
            )

        db_department = DBDepartment(**department.model_dump())
        db.add(db_department)
        db.commit()
        db.refresh(db_department)
        return db_department
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Database constraint violation")
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred")


@router.put("/{department_id}", response_model=Department)
async def update_department(
    department_id: int,
    department: DepartmentUpdate,
    db: Session = Depends(get_db),
):
    try:
        db_department = (
            db.query(DBDepartment).filter(DBDepartment.id == department_id).first()
        )

        if not db_department:
            raise HTTPException(status_code=404, detail="Department not found")

        # Check name uniqueness if name is being updated
        if department.department and department.department != db_department.department:
            existing = (
                db.query(DBDepartment)
                .filter(DBDepartment.department == department.department)
                .first()
            )
            if existing:
                raise HTTPException(
                    status_code=400, detail="Department name already exists"
                )

        # Update only provided fields
        update_data = department.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_department, field, value)

        db.commit()
        db.refresh(db_department)
        return db_department
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Database constraint violation")
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred")


@router.delete("/{department_id}", status_code=204)
async def delete_department(
    department_id: int,
    db: Session = Depends(get_db),
):
    try:
        db_department = (
            db.query(DBDepartment).filter(DBDepartment.id == department_id).first()
        )

        if not db_department:
            raise HTTPException(status_code=404, detail="Department not found")

        db.delete(db_department)
        db.commit()
        return Response(status_code=204)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Database constraint violation")
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred")


@router.post("/upload", response_model=UploadResponse)
async def upload_departments_csv(
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
        df.columns = ["id", "department"]

        # Validate data
        if df.isnull().any().any():
            raise HTTPException(status_code=400, detail="CSV contains null values")

        records_inserted = 0
        records_updated = 0

        for _, row in df.iterrows():
            existing = (
                db.query(DBDepartment).filter(DBDepartment.id == int(row["id"])).first()
            )

            if existing:
                existing.department = row["department"]
                records_updated += 1
            else:
                dept = DBDepartment(id=int(row["id"]), department=row["department"])
                db.add(dept)
                records_inserted += 1

        db.commit()

        return UploadResponse(
            message="Departments uploaded successfully",
            records_inserted=records_inserted,
            records_updated=records_updated,
        )
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="CSV file is empty")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@router.post("/upload/batch", response_model=BatchResponse)
def batch_insert_departments(
    departments: List[Department], db: Session = Depends(get_db)
):
    if len(departments) < 1 or len(departments) > 1000:
        raise HTTPException(
            status_code=400, detail="Batch size must be between 1 and 1000 records"
        )

    try:
        records_inserted = 0
        bulk_dept = []

        for dept_data in departments:
            dept = DBDepartment(**dept_data.model_dump())
            bulk_dept.append(dept)
            records_inserted += 1

        db.bulk_save_objects(bulk_dept)
        db.commit()

        return BatchResponse(
            message="Batch insert successful", records_processed=records_inserted
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
