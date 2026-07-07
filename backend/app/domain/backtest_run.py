from dataclasses import dataclass, field
from datetime import date
from uuid import uuid4

from app.domain.account import Account
from app.domain.asset import Asset


@dataclass
class BacktestRun:
    account: Account
    asset: Asset
    strategy_name: str
    start_date: date
    end_date: date
    initial_capital: float
    run_id: str = field(default_factory=lambda: str(uuid4()))
