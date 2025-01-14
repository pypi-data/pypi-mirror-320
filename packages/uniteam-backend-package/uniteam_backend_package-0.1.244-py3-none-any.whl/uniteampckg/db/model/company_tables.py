from typing import List, Optional, Dict
from datetime import datetime
from uniteampckg.db.model.db_base_model import BaseTableModel, Column


class Company(BaseTableModel):
    company_id: Optional[str] = Column(primary_key=True)
    company_name: str = Column()
    admin_user_id: str = Column()
    admin_f_name: str = Column()
    admin_l_name: str = Column()
    admin_email: str = Column()
    finch_company_id: Optional[str] = Column()
    finch_access_key: Optional[str] = Column()
    hr_sync_status: Optional[str] = Column()
    hr_sync_date: Optional[str] = Column()
    number_of_employees: Optional[int] = Column()
    tango_customer_id: Optional[str] = Column()
    tango_account_id: Optional[str] = Column()
    unsynced_employees: Optional[List[str]] = Column()
    joined_at: datetime = Column()
    finch_connection_id: Optional[str] = Column()
    hr_conn_status: Optional[str] = Column()
    hris_enabled: Optional[bool] = Column()


class CompanyConfig(BaseTableModel):
    company_id: str = Column(
        primary_key=True, foreign_key_column="company_id", foreign_key_table="company"
    )
    company_name: Optional[str] = Column()
    company_logo: Optional[str] = Column()
    color_pallete: Optional[str] = Column()
    subdomain: Optional[str] = Column()
    custom_domain: Optional[str] = Column()
    domain_settings: Optional[Dict] = Column()
    available_redeem_options: Optional[Dict] = Column()
    giftcard_vendors: Optional[Dict] = Column()
    maximum_spent: Optional[Dict] = Column()
    maximum_cart_value: Optional[Dict] = Column()
    employee_connection_info: Optional[Dict] = Column()
    employee_register_status_tracker: Optional[Dict] = Column()
    selected_departments: Optional[List[str]] = Column()
    auth_type: str = Column(default="EMAIL_PASS")
    sso_conn_id: Optional[str] = Column()
    is_all_emp_sync_enabled: Optional[bool] = Column()


class CompanyValues(BaseTableModel):
    value_id: str = Column(primary_key=True)
    company_id: str = Column()
    icon_url: str = Column()
    value_name: str = Column()
    value_description: str = Column()
    background_color: str = Column()
    text_color: str = Column()


class Department(BaseTableModel):
    company_id: Optional[str] = Column(
        foreign_key_column="company_id", foreign_key_table="company"
    )
    finch_company_id: Optional[str] = Column()
    department_id: str = Column(primary_key=True)
    department_name: Optional[str] = Column()
    parent_name: Optional[str] = Column()
    parent_id: Optional[str] = Column()
    hris_selected: Optional[bool] = Column()


class CompanyModuleMap(BaseTableModel):
    company_id: str = Column(
        foreign_key_column="company_id", foreign_key_table="company", primary_key=True
    )
    module_feed: Optional[Dict] = Column()
    module_connect: Optional[Dict] = Column()
    module_survey: Optional[Dict] = Column()
    module_contest: Optional[Dict] = Column()
    module_recognition: Optional[Dict] = Column()
    module_events: Optional[Dict] = Column()
    module_analytics: Optional[Dict] = Column()
    module_shop: Optional[Dict] = Column()
    module_notification: Optional[Dict] = Column()
    module_user_management: Optional[Dict] = Column()
    module_authentication: Optional[Dict] = Column()
    hris_intergration: Optional[Dict] = Column()
    role_based_access: Optional[Dict] = Column()
    auto_user_grouping: Optional[Dict] = Column()
    auth_email: Optional[Dict] = Column()
    auth_sso: Optional[Dict] = Column()
    custom_branding: Optional[Dict] = Column()
    custom_color_theme: Optional[Dict] = Column()
    feed_story: Optional[Dict] = Column()
    feed_community: Optional[Dict] = Column()
    feed_recognition: Optional[Dict] = Column()
    feed_polls: Optional[Dict] = Column()
    feed_profanity_check: Optional[Dict] = Column()
    connect_dms: Optional[Dict] = Column()
    connect_space: Optional[Dict] = Column()
    connect_huddle: Optional[Dict] = Column()
    connect_meet: Optional[Dict] = Column()
    connect_threads: Optional[Dict] = Column()
    connect_campaigns: Optional[Dict] = Column()
    connect_recognition: Optional[Dict] = Column()
    survey_recurring: Optional[Dict] = Column()
    notification_emails: Optional[Dict] = Column()
    notification_sms: Optional[Dict] = Column()
    notification_push: Optional[Dict] = Column()
    shop_custom_catalog: Optional[Dict] = Column()
    shop_gitf_card: Optional[Dict] = Column()
    shop_donation: Optional[Dict] = Column()
    shop_prepaid_points: Optional[Dict] = Column()
    auto_occasion: Optional[Dict] = Column()
