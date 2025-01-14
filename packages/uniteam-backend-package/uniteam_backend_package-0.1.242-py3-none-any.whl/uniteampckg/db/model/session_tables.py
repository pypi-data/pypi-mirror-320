from typing import Optional, Dict, List
from uniteampckg.db.model import BaseTableModel, Column
from datetime import datetime


class Sessions(BaseTableModel):
    session_id: str = Column(primary_key=True)
    employee_id: str = Column(
        foreign_key_column="employee_id", foreign_key_table="employee"
    )
    company_id: str = Column(
        foreign_key_column="company_id", foreign_key_table="company"
    )
    access_token: str = Column()
    refresh_token: str = Column()
    last_login: datetime = Column()


class RoleConnection(BaseTableModel):
    role_connection_key: str = Column(primary_key=True)
    role_id: Optional[str] = Column(
        foreign_key_column="role_id", foreign_key_table="role_table"
    )
    group_id: Optional[str] = Column(
        foreign_key_column="group_id", foreign_key_table="group_table"
    )
    employee_id: Optional[str] = Column(
        foreign_key_column="employee_id", foreign_key_table="employee"
    )
    company_id: Optional[str] = Column(
        foreign_key_column="company_id", foreign_key_table="company"
    )
    origin: Optional[str] = Column()


class RoleTable(BaseTableModel):
    company_id: Optional[str] = Column(
        foreign_key_column="company_id", foreign_key_table="company"
    )
    role_id: str = Column(primary_key=True)
    role_name: Optional[str] = Column()
    description: Optional[str] = Column()
    access_homepage: Optional[bool] = Column()
    access_celebrate: Optional[bool] = Column()
    access_rewards: Optional[bool] = Column()
    access_survey: Optional[bool] = Column()
    access_contest: Optional[bool] = Column()
    access_chat: Optional[bool] = Column()
    access_settings: Optional[bool] = Column()
    view_employee_account: Optional[bool] = Column()
    add_employee_account: Optional[bool] = Column()
    company_ad_connect: Optional[bool] = Column()
    edit_employee_account: Optional[bool] = Column()
    deactivate_employee_account: Optional[bool] = Column()
    view_role_permissions: Optional[bool] = Column()
    add_role_permissions: Optional[bool] = Column()
    edit_role_permissions: Optional[bool] = Column()
    delete_role_permissions: Optional[bool] = Column()
    view_group: Optional[bool] = Column()
    add_group: Optional[bool] = Column()
    edit_group: Optional[bool] = Column()
    delete_group: Optional[bool] = Column()
    edit_domain_settings: Optional[bool] = Column()
    edit_company_branding: Optional[bool] = Column()
    edit_auth_config: Optional[bool] = Column()
    edit_home_screen_layout: Optional[bool] = Column()
    create_point_distribution: Optional[bool] = Column()
    view_point_distribution: Optional[bool] = Column()
    view_point_purchase: Optional[bool] = Column()
    purchase_points_diamond: Optional[bool] = Column()
    purchase_points_gold: Optional[bool] = Column()
    view_plan: Optional[bool] = Column()
    view_user_reports: Optional[bool] = Column()
    recognize_celebrate_post: Optional[bool] = Column()
    view_recent_recognitions: Optional[bool] = Column()
    view_upcoming_activities: Optional[bool] = Column()
    create_celebrate_post: Optional[bool] = Column()
    comment_on_posts: Optional[bool] = Column()
    like_posts: Optional[bool] = Column()
    celeb_upload_image: Optional[bool] = Column()
    celeb_upload_video: Optional[bool] = Column()
    celeb_upload_gif: Optional[bool] = Column()
    celeb_attach_external_media: Optional[bool] = Column()
    shop_gift_cards: Optional[bool] = Column()
    shop_donation: Optional[bool] = Column()
    shop_custom_gifts: Optional[bool] = Column()
    create_survey: Optional[bool] = Column()
    view_survey: Optional[bool] = Column()
    take_survey: Optional[bool] = Column()
    recognize_chat: Optional[bool] = Column()
    chat_upload_image: Optional[bool] = Column()
    chat_upload_video: Optional[bool] = Column()
    chat_upload_gif: Optional[bool] = Column()
    chat_attach_external_media: Optional[bool] = Column()
    view_recognition_types: Optional[bool] = Column()
    create_recognition_types: Optional[bool] = Column()
    edit_recognition_types: Optional[bool] = Column()
    delete_recognition_types: Optional[bool] = Column()
    view_custom_gift_cards: Optional[bool] = Column()
    create_custom_gift_cards: Optional[bool] = Column()
    edit_custom_gift_cards: Optional[bool] = Column()
    delete_custom_gift_cards: Optional[bool] = Column()
    view_custom_gift_card_orders: Optional[bool] = Column()
    created_at: Optional[datetime] = Column(default=datetime.utcnow)
    last_modified_at: Optional[datetime] = Column(default=datetime.utcnow)
    is_default: Optional[bool] = Column()
    create_contest: Optional[bool] = Column()
    participate_contest: Optional[bool] = Column()
    create_chat_space: Optional[bool] = Column()
    browse_chat_space: Optional[bool] = Column()
    create_community: Optional[bool] = Column()
    criteria: Optional[Dict] = Column()
    employees: Optional[List[str]] = Column()
    groups: Optional[List[str]] = Column()
