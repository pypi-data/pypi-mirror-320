from typing import Optional, Dict, List
from datetime import datetime
from uniteampckg.db.model.db_base_model import BaseTableModel, Column


class Transaction(BaseTableModel):
    transaction_id: str = Column(primary_key=True)
    employee_id: Optional[str] = Column()
    session_id: str = Column(primary_key=True)
    company_id: Optional[str] = Column(
        foreign_key_column="company_id", foreign_key_table="company"
    )
    customer_id: Optional[str] = Column()
    amount_total: Optional[int] = Column()
    amount_subtotal: Optional[int] = Column()
    point_quantity: Optional[int] = Column()
    currency: Optional[str] = Column()
    bucket_name: Optional[str] = Column()
    checkout_status: Optional[str] = Column()
    payment_method: Optional[str] = Column()
    payment_status: Optional[str] = Column()
    receipt_url: Optional[str] = Column()
    customer_postal_code: Optional[str] = Column()
    customer_country: Optional[str] = Column()
    failure_code: Optional[str] = Column()
    failure_message: Optional[str] = Column()
    transaction_at: Optional[str] = Column()

    __primary_key__ = ["session_id", "transaction_id"]


class TransactionBin(BaseTableModel):
    transaction_id: Optional[str] = Column()
    employee_id: Optional[str] = Column()
    session_id: str = Column(primary_key=True)
    company_id: Optional[str] = Column(
        foreign_key_column="company_id", foreign_key_table="company"
    )
    customer_id: Optional[str] = Column()
    amount_total: Optional[int] = Column()
    amount_subtotal: Optional[int] = Column()
    point_quantity: Optional[int] = Column()
    currency: Optional[str] = Column()
    bucket_name: Optional[str] = Column()
    checkout_status: Optional[str] = Column()
    payment_status: Optional[str] = Column()
    payment_method: Optional[str] = Column()
    receipt_url: Optional[str] = Column()
    customer_postal_code: Optional[str] = Column()
    customer_country: Optional[str] = Column()
    failure_code: Optional[str] = Column()
    failure_message: Optional[str] = Column()
    transaction_at: Optional[str] = Column()
