from typing import Optional, Dict, List
from datetime import datetime
from uniteampckg.db.model.db_base_model import BaseTableModel, Column


class ShopOrderHead(BaseTableModel):
    company_id: str = Column(
        foreign_key_column="company_id", foreign_key_table="company"
    )
    employee_id: str = Column(
        foreign_key_column="employee_id", foreign_key_table="employee"
    )
    order_id: str = Column(primary_key=True)
    quantity: int = Column()
    total_amount: int = Column()
    currency: Optional[str] = Column()
    total_points: int = Column()
    created_at: Optional[str] = Column()


class ShopOrderLine(BaseTableModel):
    line_item_id: Optional[str] = Column()
    order_id: str = Column(
        foreign_key_column="order_id", foreign_key_table="shop_order_head"
    )
    reference_order_id: Optional[str] = Column()
    amount: int = Column()
    points: int = Column()
    value_type: Optional[str] = Column()
    brand_name: Optional[str] = Column()
    brand_id: Optional[str] = Column()
    utid: Optional[str] = Column()
    reward_name: Optional[str] = Column()
    image_url: Optional[str] = Column()
    type: Optional[str] = Column()
    created_at: Optional[str] = Column()


class CustomGiftcard(BaseTableModel):
    company_id: str = Column()
    giftcard_id: str = Column(primary_key=True)
    giftcard_title: str = Column()
    giftcard_description: str = Column()
    giftcard_image: str = Column()
    points: int = Column()
    created_time: datetime = Column()
    created_by: str = Column()
