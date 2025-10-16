from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional

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
    datetime: Optional[str] = None
    department_id: Optional[int] = None
    job_id: Optional[int] = None


class EmployeeBasic(EmployeeBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class EmployeeCreate(EmployeeBase):
    pass


class Employee(EmployeeBase):
    id: int
    department: Optional[Department] = None

    model_config = ConfigDict(from_attributes=True)


class EmployeeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    department_id: Optional[int] = Field(None, gt=0)
    position: Optional[str] = Field(None, min_length=1, max_length=100)
    salary: Optional[float] = Field(None, gt=0)


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
