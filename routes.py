import logging

from fastapi import APIRouter
from fastapi import UploadFile
from sqlmodel import Session, select

import pandas as pd
from sqlalchemy.exc import IntegrityError
from models import Company, Employee, engine


router = APIRouter()

@router.post("/upload/")
async def upload_excel(file: UploadFile ):
    df = pd.read_excel(file.file,header=0)
    df.rename(columns={"EMPLOYEE_ID": "employee_id", "FIRST_NAME": "first_name", "LAST_NAME": "last_name",
                        "PHONE_NUMBER": "phone_number", "COMPANY_NAME": "name", "SALARY": "salary",
                        "MANAGER_ID": "manager_id", "DEPARTMENT_ID": "department_id"},
              inplace=True)

    df_unique = df[['name']].drop_duplicates()
    company_list = df_unique.to_dict(orient='records')
    # skipping the validation as we have small kind of test.
    with Session(engine) as session:
        try:
            existing_companies = session.exec(select(Company.name)).all()
            existing_names = set(existing_companies)
            new_companies = [c for c in company_list if c['name'] not in existing_names]
            if new_companies:
                session.bulk_insert_mappings(Company, new_companies)
                session.commit()
                # performing bulk create to avoid N+1 transaction problem
            companies = session.exec(select(Company.id, Company.name)).all()
            company_df = pd.DataFrame(companies, columns=['company_id', 'name'])

            df = df.merge(company_df, on='name', how='left')
            df = df.drop(columns=['name'])
            employees = df.to_dict(orient='records')

            session.bulk_insert_mappings(Employee, employees)
            session.commit()
        except IntegrityError as _ex:
            logging.error(f"Failed to insert employees due to integrity error: {_ex}")
            return {"status": "partial fail", "message": "Some employee details are duplicates."}
    return {"status": "success", "companies": len(companies), "employees": len(employees)}