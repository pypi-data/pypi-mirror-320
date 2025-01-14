from typing import Optional, List, Dict
from datetime import datetime
from uniteampckg.db.model.db_base_model import BaseTableModel, Column


class PlatformColorTheme(BaseTableModel):
    theme_id: str = Column(primary_key=True)
    theme_name: str = Column()
    description: Optional[str] = Column()
    preview_img: Optional[str] = Column()
    pallete_colors: List[str] = Column()
    created_at: datetime = Column(default=datetime.utcnow)
    company_id: Optional[str] = Column(
        foreign_key_column="company_id", foreign_key_table="company"
    )
    is_default: bool = Column(default=False)
    is_global: bool = Column(default=False)


class HomeScreen(BaseTableModel):
    company_id: str = Column(
        foreign_key_column="company_id", foreign_key_table="company", primary_key=True
    )
    month: str = Column(primary_key=True)
    year: str = Column(primary_key=True)
    screen_config: Optional[Dict] = Column()
    mobile_screen_config: Optional[Dict] = Column()
