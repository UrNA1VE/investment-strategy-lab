from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4
from app.domain.portfolio import Portfolio


@dataclass
class Account:
    name: str
    account_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    portfolios: dict[str, Portfolio] = field(default_factory=dict)

    @classmethod
    def demo(cls) -> "Account":
        return cls(name="Demo Account")
    
    def create_portfolio(self, name: str, cash: float) -> None:
        if name in self.portfolios:
            raise ValueError(f'{name} found in existing portfolio names, please choose a different name')
        self.portfolios[name] = Portfolio(cash = cash)
    
    def assign_initial_capital(self, name: str, new_capital: float) -> None:
        if name not in self.portfolios:
            raise ValueError(f'{name} not found in existing portfolio names')
        self.portfolios[name]._change_capital(new_capital)

    def assign_initial_captical(self, name: str, new_capital: float) -> None:
        self.assign_initial_capital(name, new_capital)

    def backtest(self) -> str:
        for name in self.portfolios:
            self.portfolios[name].run()
        return "Backtest has been completed"
    
    def summary(self) -> dict:
        portfolio_summaries = {
            name: portfolio.summary()
            for name, portfolio in self.portfolios.items()
        }

        total_initial_capital = sum(
            summary["initial_capital"]
            for summary in portfolio_summaries.values()
        )
        total_final_value = sum(
            summary["final_value"]
            for summary in portfolio_summaries.values()
        )
        total_pnl = total_final_value - total_initial_capital
        total_return = (
            total_pnl / total_initial_capital
            if total_initial_capital
            else 0.0
        )
        total_trade_count = sum(
            summary["trade_count"]
            for summary in portfolio_summaries.values()
        )

        return {
            "account_id": self.account_id,
            "name": self.name,
            "portfolio_count": len(self.portfolios),
            "total_initial_capital": total_initial_capital,
            "total_final_value": total_final_value,
            "total_pnl": total_pnl,
            "total_return": total_return,
            "total_trade_count": total_trade_count,
            "portfolios": portfolio_summaries,
        }

        
