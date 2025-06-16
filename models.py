# models.py
from sqlmodel import SQLModel, Field, create_engine, Relationship
from typing import Optional, List

class Company(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    employees: List["Employee"] = Relationship(back_populates="company")

class Employee(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    employee_id: str = Field(unique=True)
    first_name: str
    last_name: str
    salary: int
    department_id: int

    phone_number: str
    company_id: Optional[int] = Field(default=None, foreign_key="company.id")
    company: Optional[Company] = Relationship(back_populates="employees")

# Create DB
engine = create_engine("sqlite:///data.db")

def create_db():
    SQLModel.metadata.create_all(engine)
