from typing import List, Optional, Dict
from datetime import datetime
from uniteampckg.db.model.db_base_model import BaseTableModel, Column


class CallRoom(BaseTableModel):
    company_id: Optional[str] = Column(
        foreign_key_column="company_id", foreign_key_table="company"
    )
    call_room_id: str = Column(primary_key=True)
    created_at: Optional[str] = Column()
    created_by: Optional[str] = Column(
        foreign_key_column="employee_id", foreign_key_table="employee"
    )
    room_type: Optional[str] = Column()
    room_scope: Optional[str] = Column()
    room_display_name: Optional[str] = Column()
    room_status: Optional[str] = Column()


class CallRoomEmpConnection(BaseTableModel):
    company_id: Optional[str] = Column(
        foreign_key_column="company_id", foreign_key_table="company"
    )
    call_room_emp_conn_id: Optional[str] = Column()
    call_room_id: Optional[str] = Column(
        foreign_key_column="call_room_id", foreign_key_table="call_room"
    )
    employee_id: Optional[str] = Column(
        foreign_key_column="employee_id", foreign_key_table="employee"
    )
    role: Optional[str] = Column()
    join_status: Optional[str] = Column()
    joined_at: Optional[str] = Column()
