from typing import Optional, List, Dict
from datetime import datetime, date
from uniteampckg.db.model.db_base_model import BaseTableModel, Column


class PointDistribute(BaseTableModel):
    company_id: Optional[str] = Column(
        foreign_key_column="company_id", foreign_key_table="company"
    )
    distribute_id: str = Column(primary_key=True)
    employee_list: Optional[List[str]] = Column()
    group_list: Optional[List[str]] = Column()
    points: Optional[int] = Column()
    criterias: Optional[Dict] = Column()
    distribution_type: Optional[str] = Column()
    interval_criteria: Optional[str] = Column()
    last_auto_distributed_date: Optional[date] = Column()
    next_auto_distributed_date: Optional[date] = Column()
    interval_value: Optional[str] = Column()
    created_at: Optional[date] = Column()
    bucket: Optional[str] = Column()
    created_by: Optional[str] = Column()
