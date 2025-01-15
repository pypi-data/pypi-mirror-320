from typing import List, Optional, Dict
from datetime import datetime
from uniteampckg.db.model.db_base_model import BaseTableModel, Column


class ChatSpace(BaseTableModel):
    space_id: str = Column(primary_key=True)
    company_id: str = Column(
        foreign_key_column="company_id", foreign_key_table="company"
    )
    space_name: str = Column()
    space_image: Optional[str] = Column()
    space_description: Optional[str] = Column()
    created_by: Optional[str] = Column()
    criteria: Optional[Dict] = Column()
    employees: Optional[List[str]] = Column()
    created_at: Optional[datetime] = Column()
    visibility: Optional[str] = Column()
    search_vector: Optional[str] = Column()


class ChatSpaceConnection(BaseTableModel):
    space_connection_id: str = Column(primary_key=True)
    company_id: str = Column(
        foreign_key_column="company_id", foreign_key_table="company"
    )
    space_id: str = Column(
        foreign_key_column="space_id", foreign_key_table="chat_space"
    )
    employee_id: Optional[str] = Column()
    role: Optional[str] = Column()
    origin: Optional[str] = Column()
    join_status: Optional[str] = Column()
    joined_at: Optional[datetime] = Column()


class ChatMessages(BaseTableModel):
    message_id: str = Column(primary_key=True)
    sender_id: str = Column()
    recipient_id: str = Column()
    company_id: str = Column(
        foreign_key_column="company_id", foreign_key_table="company"
    )
    is_recognition: Optional[bool] = Column()
    recognition_id: Optional[str] = Column()
    sent_time: Optional[datetime] = Column()
    messages: Optional[str] = Column()
    media: Optional[Dict] = Column()
    message_type: Optional[str] = Column()
    audio: Optional[str] = Column()
    entity_type: Optional[str] = Column()
    space_id: Optional[str] = Column(
        foreign_key_column="space_id", foreign_key_table="chat_space"
    )
    is_archived: Optional[bool] = Column()
    poll_id: Optional[str] = Column()
    message_rich_text: Optional[str] = Column()
    message_rich_html_content: Optional[str] = Column()
    video: Optional[str] = Column()
    employee_mentions: Optional[List[str]] = Column()
    value_mentions: Optional[List[str]] = Column()
    parent_thread_id: Optional[str] = Column()
    is_quote: Optional[bool] = Column()
    quote_message_id: Optional[str] = Column()
    is_forwarded: Optional[bool] = Column()
    forwarded_message_id: Optional[str] = Column()
    is_broadcast: Optional[bool] = Column()
    broadcast_message_id: Optional[str] = Column()
    campaign_id: Optional[str] = Column()
    meeting_room_id: Optional[str] = Column()


class ChatConnection(BaseTableModel):
    user_id: str = Column()
    connection_id: str = Column(primary_key=True)


class ChatSubSpace(BaseTableModel):
    sub_space_id: str = Column(primary_key=True)
    space_id: str = Column(
        foreign_key_column="space_id", foreign_key_table="chat_space"
    )
    company_id: str = Column(
        foreign_key_column="company_id", foreign_key_table="company"
    )
    sub_space_name: str = Column()
    sub_space_description: Optional[str] = Column()
    is_default: Optional[bool] = Column()
    can_message: Optional[str] = Column()
    created_at: Optional[datetime] = Column()


class SpaceJoinStatus(BaseTableModel):
    space_join_status_id: str = Column(primary_key=True)
    space_id: str = Column(
        foreign_key_column="space_id", foreign_key_table="chat_space"
    )
    company_id: Optional[str] = Column(
        foreign_key_column="company_id", foreign_key_table="company"
    )
    employee_id: Optional[str] = Column(
        foreign_key_column="employee_id", foreign_key_table="employee"
    )
    join_status: Optional[str] = Column()
    requested_at: Optional[str] = Column()


class MessageStatus(BaseTableModel):
    message_status_id: str = Column(primary_key=True)
    message_id: str = Column(
        foreign_key_column="message_id", foreign_key_table="chat_messages"
    )
    recipient_id: str = Column(
        foreign_key_column="employee_id", foreign_key_table="employee"
    )
    company_id: str = Column(
        foreign_key_column="company_id", foreign_key_table="company"
    )
    is_delivered: Optional[bool] = Column()
    is_seen: Optional[bool] = Column()
    delivered_time: Optional[str] = Column()
    seen_time: Optional[str] = Column()


class Campaign(BaseTableModel):
    campaign_id: str = Column(primary_key=True)
    company_id: str = Column(
        foreign_key_column="company_id", foreign_key_table="company"
    )
    campaign_title: str = Column()
    created_at: Optional[datetime] = Column()
    created_by: str = Column(
        foreign_key_column="employee_id", foreign_key_table="employee"
    )
    employees: Optional[List[str]] = Column()
    criteria: Optional[Dict] = Column()
