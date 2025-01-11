from typing import Optional
from uniteampckg.db.model import BaseTableModel, Column
from datetime import datetime


class Employee(BaseTableModel):
    company_id: Optional[str] = Column(
        foreign_key_table="company", foreign_key_column="company_id"
    )
    employee_id: str = Column(primary_key=True)
    finch_individual_id: Optional[str] = Column()
    employee_number: Optional[str] = Column()
    org_mem_id: Optional[str] = Column()
    first_name: Optional[str] = Column()
    last_name: Optional[str] = Column()
    position_title: Optional[str] = Column()
    employment_type: Optional[str] = Column()
    employment_subtype: Optional[str] = Column()
    gender: Optional[str] = Column()
    dob: Optional[datetime] = Column()
    manager_id: Optional[str] = Column()
    work_email_id: Optional[str] = Column()
    personal_email_id: Optional[str] = Column()
    work_phone: Optional[str] = Column()
    personal_phone: Optional[str] = Column()
    employment_city: Optional[str] = Column()
    state: Optional[str] = Column()
    postal_code: Optional[str] = Column()
    country: Optional[str] = Column()
    org_level_1: Optional[str] = Column()
    org_level_2: Optional[str] = Column()
    org_level_3: Optional[str] = Column()
    employment_state: Optional[str] = Column()
    employment_country: Optional[str] = Column()
    employment_postal_code: Optional[str] = Column()
    stripe_customer_id: Optional[str] = Column()
    department: Optional[str] = Column()
    bio: Optional[str] = Column()
    joined_on: Optional[datetime] = Column()
    latest_rehire_date: Optional[datetime] = Column()
    is_active: Optional[bool] = Column()
    password: Optional[str] = Column()
    profile_url: Optional[str] = Column()
    created_by: Optional[str] = Column()
    department_id: Optional[str] = Column()
    employment_line1: Optional[str] = Column()
    employment_line2: Optional[str] = Column()
    location_id: Optional[str] = Column()
    income_amount: Optional[int] = Column()
    employee_status: Optional[dict] = Column()
    employee_interest: Optional[list] = Column()
    employee_account_status: Optional[str] = Column()
    search_vector: Optional[str] = Column()


class EmployeePointsTracker(BaseTableModel):
    employee_id: str = Column(
        primary_key=True, foreign_key_column="employee_id", foreign_key_table="employee"
    )
    company_id: Optional[str] = Column(
        foreign_key_column="company_id", foreign_key_table="company"
    )
    diamond_bucket: Optional[int] = Column()
    golden_bucket: Optional[int] = Column()
    no_of_recognition_received: Optional[int] = Column()
    no_of_recognition_given: Optional[int] = Column()


class GroupTable(BaseTableModel):
    company_id: Optional[str] = Column(
        foreign_key_column="company_id", foreign_key_table="company"
    )
    group_id: str = Column(primary_key=True)
    group_name: Optional[str] = Column()
    group_image: Optional[str] = Column()
    created_at: Optional[datetime] = Column()
    created_by: Optional[str] = Column()
    last_modified_at: Optional[datetime] = Column()
    description: Optional[str] = Column()
    criteria: Optional[str] = Column()
    employees: Optional[list[str]] = Column()


class GroupConnection(BaseTableModel):
    group_connection_key: str = Column(primary_key=True)
    group_id: Optional[str] = Column(
        foreign_key_column="group_id", foreign_key_table="group_table"
    )
    employee_id: Optional[str] = Column(
        foreign_key_column="employee_id", foreign_key_table="employee"
    )
    origin: Optional[str] = Column()


class WorkLocation(BaseTableModel):
    company_id: str = Column()
    location_id: str = Column(primary_key=True)
    location_name: Optional[str] = Column()
    line_1: Optional[str] = Column()
    line_2: Optional[str] = Column()
    city: Optional[str] = Column()
    state: Optional[str] = Column()
    country: Optional[str] = Column()
    postal_code: Optional[str] = Column()
