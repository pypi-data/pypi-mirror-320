from typing import Optional, Dict, List
from datetime import datetime, date
from uniteampckg.db.model.db_base_model import BaseTableModel, Column


class Celebrate(BaseTableModel):
    post_id: str = Column(primary_key=True)
    employee_id: Optional[str] = Column(
        foreign_key_column="employee_id", foreign_key_table="employee"
    )
    company_id: Optional[str] = Column(
        foreign_key_column="company_id", foreign_key_table="company"
    )
    is_main_post: Optional[str] = Column()
    parent_id: Optional[str] = Column()
    is_recognition: Optional[bool] = Column()
    recognition_id: Optional[str] = Column(
        foreign_key_column="recognition_id", foreign_key_table="recognitions"
    )
    post_content: Optional[str] = Column()
    like_count: Optional[int] = Column()
    comment_count: Optional[int] = Column()
    posted_at: Optional[datetime] = Column()
    media: Optional[Dict] = Column()
    is_archive: Optional[bool] = Column()
    mentions: Optional[Dict] = Column()
    post_scope: Optional[str] = Column()
    community_id: Optional[str] = Column()
    poll_id: Optional[str] = Column()
    occasion_history_id: Optional[str] = Column()
    is_occasion: Optional[bool] = Column()


class LikeTable(BaseTableModel):
    like_id: str = Column(primary_key=True)
    post_id: Optional[str] = Column(
        foreign_key_column="post_id", foreign_key_table="celebrate"
    )
    liked_by: Optional[str] = Column(
        foreign_key_column="employee_id", foreign_key_table="employee"
    )
    liked_at: Optional[date] = Column()


class PostViews(BaseTableModel):
    employee_id: str = Column(
        foreign_key_column="employee_id", foreign_key_table="employee", primary_key=True
    )
    company_id: str = Column(
        foreign_key_column="company_id", foreign_key_table="company", primary_key=True
    )
    post_id: str = Column(
        foreign_key_column="post_id", foreign_key_table="celebrate", primary_key=True
    )
    seen: Optional[bool] = Column(default=False)


class Reaction(BaseTableModel):
    reaction_id: str = Column(primary_key=True)
    company_id: str = Column(
        foreign_key_column="company_id", foreign_key_table="company"
    )
    message_id: Optional[str] = Column(
        foreign_key_column="message_id", foreign_key_table="chat_messages"
    )
    reacted_employee: str = Column(
        foreign_key_column="employee_id", foreign_key_table="employee"
    )
    reaction: Optional[str] = Column()
    reacted_at: Optional[datetime] = Column()
    post_id: Optional[str] = Column(
        foreign_key_column="post_id", foreign_key_table="celebrate"
    )
    reaction_asci: Optional[str] = Column()
    call_room_id: Optional[str] = Column()


class FlaggedPost(BaseTableModel):
    flagged_id: str = Column(primary_key=True)
    post_id: str = Column()
    reporter_id: str = Column()
    flagged_reason: str = Column()
    flagged_description: str = Column()
    flagged_at: datetime = Column(default=datetime.utcnow)
    status: str = Column()
    flagged_type: str = Column()


# community


class Community(BaseTableModel):
    community_id: str = Column(primary_key=True)
    company_id: str = Column(
        foreign_key_column="company_id", foreign_key_table="company"
    )
    community_name: str = Column()
    community_icon: Optional[str] = Column()
    community_feature_image: Optional[str] = Column()
    community_desc: Optional[str] = Column()
    created_at: datetime = Column()
    employee_id: str = Column(
        foreign_key_column="employee_id", foreign_key_table="employee"
    )
    criteria: Optional[Dict] = Column()
    employees: Optional[List[str]] = Column()
    visibility: Optional[str] = Column()
    search_vector: Optional[str] = Column()
    is_all_employee_selected: Optional[bool] = Column()


class CommunityConnection(BaseTableModel):
    community_connection_id: str = Column(primary_key=True)
    community_id: str = Column(
        foreign_key_column="community_id", foreign_key_table="community"
    )
    company_id: str = Column(
        foreign_key_column="company_id", foreign_key_table="company"
    )
    employee_id: str = Column(
        foreign_key_column="employee_id", foreign_key_table="employee"
    )
    role: str = Column()
    join_status: Optional[str] = Column()
    joined_at: datetime = Column()
    origin: Optional[str] = Column()


class CommunityJoinStatus(BaseTableModel):
    community_join_status_id: str = Column(primary_key=True)
    community_id: str = Column(
        foreign_key_column="community_id", foreign_key_table="community"
    )
    company_id: Optional[str] = Column(
        foreign_key_column="company_id", foreign_key_table="company"
    )
    employee_id: Optional[str] = Column(
        foreign_key_column="employee_id", foreign_key_table="employee"
    )
    join_status: Optional[str] = Column()
    requested_at: Optional[datetime] = Column()


# story


class Story(BaseTableModel):
    story_id: str = Column(primary_key=True)
    media_url: Optional[str] = Column()
    company_id: str = Column(
        foreign_key_column="company_id", foreign_key_table="company"
    )
    media_type: Optional[str] = Column()
    created_by: Optional[str] = Column(
        foreign_key_column="employee_id", foreign_key_table="employee"
    )
    story_caption: Optional[str] = Column()
    created_at: Optional[datetime] = Column(default=datetime.utcnow)
