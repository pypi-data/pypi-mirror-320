from typing import Optional
from uniteampckg.db.model.db_base_model import BaseTableModel, Column
from datetime import datetime


class EmployeeDeviceLink(BaseTableModel):
    company_id: Optional[str] = Column(
        foreign_key_table="company", foreign_key_column="company_id"
    )
    employee_id: Optional[str] = Column(
        foreign_key_table="employee", foreign_key_column="employee_id"
    )
    device_id: Optional[str] = Column(primary_key=True)
    fcm_token: Optional[str] = Column()
    last_used_at: Optional[datetime] = Column()
    first_registered_at: Optional[datetime] = Column()
    notification_allowed: Optional[bool] = Column()
    video_allowed: Optional[bool] = Column()
    mic_allowed: Optional[bool] = Column()


class Notification(BaseTableModel):
    company_id: Optional[str] = Column(
        foreign_key_table="company", foreign_key_column="company_id"
    )
    notification_id: Optional[str] = Column(primary_key=True)
    notification_type: Optional[str] = Column()
    created_at: Optional[datetime] = Column()
    in_app: Optional[bool] = Column()
    push: Optional[bool] = Column()
    email: Optional[bool] = Column()
    sms: Optional[bool] = Column()
    in_app_payload: Optional[dict] = Column()
    email_template: Optional[dict] = Column()
    email_payload: Optional[dict] = Column()
    push_payload: Optional[dict] = Column()
    sms_payload: Optional[dict] = Column()
    ack_status: Optional[str] = Column()
    add_to_email_summary: Optional[bool] = Column()


class NotificationRecipientLink(BaseTableModel):
    company_id: Optional[str] = Column(
        foreign_key_table="company", foreign_key_column="company_id", primary_key=True
    )
    notification_id: Optional[str] = Column(
        foreign_key_table="notification",
        foreign_key_column="notification_id",
        primary_key=True,
    )
    recipient_id: Optional[str] = Column(
        foreign_key_table="employee", foreign_key_column="employee_id", primary_key=True
    )
    ack_status: Optional[str] = Column()


class PushNotificationLog(BaseTableModel):
    company_id: Optional[str] = Column(
        foreign_key_table="company", foreign_key_column="company_id"
    )
    notification_id: Optional[str] = Column(
        foreign_key_table="notification", foreign_key_column="notification_id"
    )
    recipient_id: Optional[str] = Column(
        foreign_key_table="employee", foreign_key_column="employee_id"
    )
    device_id: Optional[str] = Column(
        foreign_key_table="employee_device_link", foreign_key_column="device_id"
    )
    sent_at: Optional[datetime] = Column()
    ack_status: Optional[str] = Column()
    log_id: Optional[str] = Column(primary_key=True)
    payload: Optional[dict] = Column()


class EmailNotificationLog(BaseTableModel):
    company_id: Optional[str] = Column(
        foreign_key_table="company", foreign_key_column="company_id"
    )
    notification_id: Optional[str] = Column(
        foreign_key_table="notification", foreign_key_column="notification_id"
    )
    recipient_id: Optional[str] = Column(
        foreign_key_table="employee", foreign_key_column="employee_id"
    )
    template_id: Optional[str] = Column()
    sent_at: Optional[datetime] = Column()
    ack_status: Optional[str] = Column()
    log_id: Optional[str] = Column(primary_key=True)
    payload: Optional[dict] = Column()


class SMSNotificationLog(BaseTableModel):
    company_id: Optional[str] = Column(
        foreign_key_table="company", foreign_key_column="company_id"
    )
    notification_id: Optional[str] = Column(
        foreign_key_table="notification", foreign_key_column="notification_id"
    )
    recipient_id: Optional[str] = Column(
        foreign_key_table="employee", foreign_key_column="employee_id"
    )
    template_id: Optional[str] = Column()
    sent_at: Optional[datetime] = Column()
    ack_status: Optional[str] = Column()
    log_id: Optional[str] = Column(primary_key=True)
    payload: Optional[dict] = Column()
