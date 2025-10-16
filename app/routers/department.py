from fastapi import APIRouter, HTTPException, Depends, Query, Response
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
