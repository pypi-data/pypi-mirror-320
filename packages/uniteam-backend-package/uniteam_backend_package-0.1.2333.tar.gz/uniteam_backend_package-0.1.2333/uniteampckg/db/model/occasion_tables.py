from typing import List, Dict, Union, Optional
from datetime import datetime, date
from uniteampckg.db.model.db_base_model import BaseTableModel, Column


class Occasion(BaseTableModel):
    company_id: str = Column()
    occasion_id: str = Column(primary_key=True)
    occasion_type: str = Column()
    points: int = Column()
    criteria: Dict = Column()
    occasion_label: str = Column()
    occasion_message: str = Column()
    occasion_banner: str = Column()
    occasion_config: Dict = Column()
    employees: List[str] = Column()
    groups: List[str] = Column()
    created_at: datetime = Column()
    created_by: str = Column()
    is_feed_post: bool = Column()
    is_all_employees_selected: bool = Column()


class OccasionHistory(BaseTableModel):
    occasion_history_id: str = Column(primary_key=True)
    company_id: str = Column(
        foreign_key_column="company_id", foreign_key_table="company"
    )
    occasion_id: str = Column()
    occasion_type: str = Column()
    points: int = Column()
    occasion_on: Optional[datetime] = Column()
    employee_id: Optional[str] = Column()
    occasion_by: Optional[str] = Column()
