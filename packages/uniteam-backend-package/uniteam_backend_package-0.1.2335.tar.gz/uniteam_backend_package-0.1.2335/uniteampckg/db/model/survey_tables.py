from typing import Optional, List, Dict
from datetime import datetime
from uniteampckg.db.model.db_base_model import BaseTableModel, Column


class Survey(BaseTableModel):
    survey_id: str = Column(primary_key=True)
    survey_name: str = Column()
    survey_description: Optional[str] = Column()
    company_id: str = Column(
        foreign_key_column="company_id", foreign_key_table="company"
    )
    creator_id: str = Column(
        foreign_key_column="creator_id", foreign_key_table="employee"
    )
    created_date: Optional[datetime] = Column()
    survey_start_date: Optional[datetime] = Column()
    survey_end_date: Optional[datetime] = Column()
    criterias: Optional[Dict] = Column()
    employees: Optional[List[str]] = Column()
    groups: Optional[List[str]] = Column()
    is_all_employees_selected: bool = Column(default=False)
    survey_feature_image: Optional[Dict] = Column()
    interval: Optional[str] = Column()
    scheduling: Optional[Dict] = Column()
    next_survey_date: Optional[datetime] = Column()
    last_survey_date: Optional[datetime] = Column()
    allow_anonymous: Optional[bool] = Column()
    search_vector: Optional[str] = Column()


class SurveyConnection(BaseTableModel):
    survey_connection_id: str = Column(primary_key=True)
    survey_id: str = Column(foreign_key_column="survey_id", foreign_key_table="survey")
    company_id: str = Column(
        foreign_key_column="company_id", foreign_key_table="company"
    )
    group_id: Optional[str] = Column()
    employee_id: Optional[str] = Column()
    is_all_employees_selected: Optional[bool] = Column()
    origin: Optional[str] = Column()


class SurveyQuestions(BaseTableModel):
    company_id: Optional[str] = Column(
        foreign_key_column="company_id", foreign_key_table="company"
    )
    survey_id: Optional[str] = Column(
        foreign_key_column="survey_id", foreign_key_table="survey"
    )
    question_id: str = Column(primary_key=True)
    question: Optional[str] = Column()
    answer_type: Optional[str] = Column()
    answer_options: Optional[Dict] = Column()


class SurveySubmission(BaseTableModel):
    submission_id: str = Column()
    survey_id: str = Column(foreign_key_column="survey_id", foreign_key_table="survey")
    submitted_at: str = Column()
    submitted_by: str = Column()
    question_id: str = Column()
    answers: Optional[Dict] = Column()
    company_id: str = Column(
        foreign_key_column="company_id", foreign_key_table="company"
    )


class SurveyTemplate(BaseTableModel):
    template_id: str = Column(primary_key=True)
    template_name: str = Column()
    survey_name: str = Column()
    survey_description: Optional[str] = Column()
    company_id: str = Column(
        foreign_key_column="company_id", foreign_key_table="company"
    )
    creator_id: str = Column(
        foreign_key_column="creator_id", foreign_key_table="employee"
    )
    created_date: Optional[str] = Column()
    criterias: Optional[Dict] = Column()
    employees: Optional[list] = Column()
    groups: Optional[list] = Column()
    is_all_employees_selected: Optional[bool] = Column(default=False)
    survey_feature_image: Optional[Dict] = Column()
    allow_anonymous: Optional[bool] = Column()


class SurveyTemplate(BaseTableModel):
    template_id: str = Column(primary_key=True)
    template_name: str = Column()
    survey_name: str = Column()
    survey_description: Optional[str] = Column()
    company_id: str = Column(
        foreign_key_column="company_id", foreign_key_table="company"
    )
    creator_id: str = Column(
        foreign_key_column="employee_id", foreign_key_table="employee"
    )
    created_date: Optional[str] = Column()
    criterias: Optional[Dict] = Column()
    employees: Optional[list] = Column()
    groups: Optional[list] = Column()
    is_all_employees_selected: Optional[bool] = Column(default=False)
    survey_feature_image: Optional[Dict] = Column()
    allow_anonymous: Optional[bool] = Column()


class SurveyTemplateQuestions(BaseTableModel):
    template_id: str = Column(
        foreign_key_column="template_id", foreign_key_table="survey_template"
    )
    question_id: str = Column(primary_key=True)
    question: Optional[str] = Column()
    answer_type: Optional[str] = Column()
    answer_options: Optional[Dict] = Column()
    is_required: Optional[bool] = Column(default=False)
    company_id: Optional[str] = Column(
        foreign_key_column="company_id", foreign_key_table="company"
    )
