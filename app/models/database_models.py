from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    department = Column(String, nullable=False)

    # Relationship
    employees = relationship("Employee", back_populates="department")

    def __repr__(self):
        return f"<Department(id={self.id}, department='{self.department}')>"


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    job = Column(String, nullable=False)

    # Relationship
    employees = relationship("Employee", back_populates="job")

    def __repr__(self):
        return f"<Job(id={self.id}, job='{self.job}')>"


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    datetime = Column(DateTime, nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)

    # Relationships
    department = relationship("Department", back_populates="employees")
    job = relationship("Job", back_populates="employees")

    def __repr__(self):
        return f"<Employee(id={self.id}, name='{self.name}')>"
