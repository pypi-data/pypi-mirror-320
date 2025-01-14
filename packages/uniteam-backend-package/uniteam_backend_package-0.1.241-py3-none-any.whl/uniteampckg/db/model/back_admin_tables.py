from typing import Optional
from uniteampckg.db.model import BaseTableModel, Column
from datetime import datetime


class BackAdmin(BaseTableModel):
    admin_id: str = Column(primary_key=True)
    email: Optional[str] = Column()
    password: Optional[str] = Column()
