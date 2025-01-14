from typing import List, Optional, Dict
from datetime import datetime
from uniteampckg.db.model.db_base_model import BaseTableModel, Column

class Contest(BaseTableModel):
    company_id: str = Column(
         foreign_key_column="company_id",foreign_key_table="company"
    )
    contest_id: str = Column(primary_key=True)
    contest_title: str = Column()
    description: str = Column()
    feature_image: str = Column()
    player_mode: str = Column()
    game_type: str = Column()
    interval_mode: str = Column()
    recurring_interval_key: str = Column()
    survival_interval: str = Column()
    created_by: str = Column()
    created_at: datetime = Column()
    start_date: datetime = Column()
    end_date: datetime = Column()
    end_on_ranks_hit: bool = Column()
    employees: List[str] = Column()
    criteria: dict = Column()
    teams: List[str] = Column()
    all_employee_selected: bool = Column()
    all_teams_selected: bool = Column()



class ContestParticipantMap(BaseTableModel):
    company_id: str = Column(
        foreign_key_table="company", foreign_key_column="company_id"
    )
    contest_id: str = Column(
        foreign_key_table="contest", foreign_key_column="contest_id"
    )
    partc_id: Optional[str] = Column(primary_key=True)
    player_type: str = Column()
    team_id: Optional[str] = Column()
    employee_id: Optional[str] = Column()
    origin: str = Column()
    is_qualified: bool = Column()


class ContestGoalMap(BaseTableModel):
    company_id: str = Column(
        foreign_key_table="company", foreign_key_column="company_id"
    )
    contest_id: str = Column(
        foreign_key_table="contest", foreign_key_column="contest_id"
    )
    goal_id: str = Column(primary_key=True)
    title: str = Column()
    goal_type: str = Column()


class ContestRankMap(BaseTableModel):
    company_id: str = Column(
        foreign_key_table="company", foreign_key_column="company_id"
    )
    contest_id: str = Column(
        foreign_key_table="contest", foreign_key_column="contest_id"
    )
    rank_id: str = Column(primary_key=True)
    rank: int = Column()
    rank_title: str = Column()
    reward_type: str = Column()
    reward_points: str = Column()
    badge_id: str = Column()
    is_participation: bool = Column()


class ContestQualificationMap(BaseTableModel):
    company_id: str = Column(
        foreign_key_table="company", foreign_key_column="company_id"
    )
    contest_id: str = Column(
        foreign_key_table="contest", foreign_key_column="contest_id"
    )
    qualification_id: str = Column(primary_key=True)
    title: str = Column()
    goal_type: str = Column()