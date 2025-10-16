from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional
from datetime import datetime

# ###############################
# Department Pydantic Models
# ###############################


class DepartmentBase(BaseModel):
    department: str = Field(..., min_length=1, max_length=150)


class Department(DepartmentBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(DepartmentBase):
    pass


# ###############################
# Job Pydantic Models
# ###############################


class JobBase(BaseModel):
    job: str = Field(..., min_length=1, max_length=150)


class Job(JobBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class JobCreate(JobBase):
    pass


class JobUpdate(JobBase):
    pass


# ###############################
# Employee Pydantic Models
# ###############################


class EmployeeBase(BaseModel):
    name: Optional[str] = None
    timestamp: Optional[datetime] = None
    department_id: Optional[int] = None
    job_id: Optional[int] = None

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_datetime(cls, v) -> Optional[datetime]:
        if v is None or v == "":
            return None

        if isinstance(v, str):
            # Parse ISO format: 2021-11-07T02:48:42Z
            dt_str = v.replace("Z", "+00:00")
            return datetime.fromisoformat(dt_str).replace(tzinfo=None)

        return v


class EmployeeBasic(EmployeeBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class Employee(EmployeeBase):
    id: int
    department: Optional[Department] = None
    job: Optional[Job] = None

    model_config = ConfigDict(from_attributes=True)


# ###############################
# RESPONSE MODELS
# ###############################


class DepartmentWithEmployees(Department):
    employees: list[EmployeeBasic] = []

    model_config = ConfigDict(from_attributes=True)


class JobWithEmployees(Job):
    employees: list[EmployeeBasic] = []

    model_config = ConfigDict(from_attributes=True)


class UploadResponse(BaseModel):
    message: str
    records_inserted: int
    records_updated: int = 0
    errors: Optional[list[str]] = None


class BatchResponse(BaseModel):
    message: str
    records_processed: int
