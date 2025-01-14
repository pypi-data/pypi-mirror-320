from typing import Optional, Dict, List
from datetime import datetime
from uniteampckg.db.model.db_base_model import BaseTableModel, Column


class PollTable(BaseTableModel):
    poll_id: str = Column(primary_key=True)
    company_id: str = Column(
        foreign_key_column="company_id", foreign_key_table="company"
    )
    poll_title: Optional[str] = Column()
    created_by: Optional[str] = Column(
        foreign_key_column="employee_id", foreign_key_table="employee"
    )
    created_at: Optional[str] = Column()


class PollOptions(BaseTableModel):
    poll_option_id: str = Column(primary_key=True)
    poll_id: str = Column(foreign_key_column="poll_id", foreign_key_table="poll_table")
    option: Optional[str] = Column()
    poll_count: Optional[int] = Column()


class PollConnection(BaseTableModel):
    poll_connection_id: str = Column(primary_key=True)
    poll_id: str = Column(foreign_key_column="poll_id", foreign_key_table="poll_table")
    poll_option_id: str = Column(
        foreign_key_column="poll_option_id", foreign_key_table="poll_options"
    )
    employee_id: str = Column(
        foreign_key_column="employee_id", foreign_key_table="employee"
    )
