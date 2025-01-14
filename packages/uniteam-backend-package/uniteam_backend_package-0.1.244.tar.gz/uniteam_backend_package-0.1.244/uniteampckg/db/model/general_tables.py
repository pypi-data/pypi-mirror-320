from typing import List, Optional, Dict
from datetime import datetime
from uniteampckg.db.model.db_base_model import BaseTableModel, Column


class ClockinConfig(BaseTableModel):
    company_id: str = Column(primary_key=True)
    enabled: bool = Column()


class ClockinConsentLogs(BaseTableModel):
    consent_log_id: str = Column(primary_key=True)
    company_id: str = Column()
    employee_id: str = Column()
    employee_name: str = Column()
    email: str = Column()
    consent_content: str = Column(nullable=True)
    consent_ts: datetime = Column(nullable=True)
    consent: str = Column(nullable=True)
    status: str = Column(nullable=True)
    country: str = Column(nullable=True)
    countrycode: str = Column(nullable=True)
    region: str = Column(nullable=True)
    regionname: str = Column(nullable=True)
    city: str = Column(nullable=True)
    zip: str = Column(nullable=True)
    lat: float = Column(nullable=True)
    lon: float = Column(nullable=True)
    timezone: str = Column(nullable=True)
    isp: str = Column(nullable=True)
    org: str = Column(nullable=True)
