from typing import Optional, Dict, List
from datetime import datetime
from uniteampckg.db.model.db_base_model import BaseTableModel, Column


class Recognitions(BaseTableModel):
    recognition_id: str = Column(primary_key=True)
    company_id: Optional[str] = Column(
        foreign_key_column="company_id", foreign_key_table="company"
    )
    recognition_by: Optional[str] = Column(
        foreign_key_column="employee_id", foreign_key_table="employee"
    )
    recognition_at: Optional[str] = Column()
    recognition_method: Optional[str] = Column()
    recognition_type: Optional[str] = Column()
    recognition_values: Optional[str] = Column()
    recognition_points: Optional[int] = Column()
    recognition_banner: Optional[str] = Column()
    recognition_total_points: Optional[int] = Column()
    recognition_point_bucket: Optional[str] = Column()


class RecognitionType(BaseTableModel):
    recognition_type_id: str = Column(primary_key=True)
    company_id: str = Column(
        foreign_key_column="company_id", foreign_key_table="company"
    )
    recognition_name: str = Column()
    description: Optional[str] = Column()
    image_url: Optional[str] = Column()
    default_points: Optional[str] = Column()
    allow_custom_point: Optional[bool] = Column()


class RecognitionConnection(BaseTableModel):
    recognition_connection_key: str = Column(primary_key=True)
    recognition_id: Optional[str] = Column(
        foreign_key_column="recognition_id", foreign_key_table="recognitions"
    )
    employee_id: Optional[str] = Column()
    group_id: Optional[str] = Column()
    from_group: Optional[bool] = Column()
    from_space: Optional[bool] = Column()
    space_id: Optional[str] = Column()


class GlobalRecognitionType(BaseTableModel):
    recognition_type_id: str = Column(primary_key=True)
    recognition_name: str = Column()
    description: str = Column()
    image_url: str = Column()
    default_points: str = Column()
    allow_custom_point: bool = Column()
