from dataclasses import dataclass, field
from typing import Any

from app.strategies.base import Signal, SignalAction
from app.domain.trade import Trade
import pandas as pd


@dataclass
class PortfolioStrategy:
    name: str
    strategy: Any

    def generate_signal(self, current_date) -> list[Signal]:
        return [
            signal.with_strategy_name(self.name)
            for signal in self.strategy.generate_signal(current_date)
        ]

    def reset_state(self) -> None:
        self.strategy.reset_state()


@dataclass
class Portfolio:
    cash: float
    initial_capital: float = 0.0
    positions: dict[str, float] = field(default_factory=dict)
    trades: list[Trade] = field(default_factory=list)
    strategies: dict[str, PortfolioStrategy] = field(default_factory=dict)
    daily_values: list[dict] = field(default_factory=list)
    latest_prices: dict[str, float] = field(default_factory=dict)

    def _change_capital(self, new_capital: float) -> None:
        self.cash = new_capital
        self.initial_capital = self.cash

    def __post_init__(self) -> None:
        self.initial_capital = self.cash

    def add_strategy(self, name: str, strategy: Any) -> None:
        self.strategies[name] = PortfolioStrategy(name=name, strategy=strategy)

    def buy_support(self, signal: Signal) -> bool:
        if self.cash is None:
            return False
        return (signal.value) <= self.cash
    
    def sell_support(self, signal: Signal) -> bool:
        return self.positions.get(signal.stock_name, 0.0) >= signal.quantity

    def sell_position(self, signal: Signal) -> None:
        self.positions[signal.stock_name] = self.positions.get(signal.stock_name, 0.0) - signal.quantity
        self.cash += signal.value
        return
    
    def add_position(self, signal) -> None:
        self.positions[signal.stock_name] = self.positions.get(signal.stock_name, 0.0) + signal.quantity
        self.cash -= signal.value
            
    def signal_to_trade(self, signal: Signal, invalid = False) -> Trade:
        if invalid:
            return Trade(signal.stock_name, signal.signal_date, SignalAction.INVALID, signal.quantity, signal.price, "Invalid signal for " + signal.strategy_name)
        return Trade(signal.stock_name, signal.signal_date, signal.action, signal.quantity, signal.price, signal.strategy_name + " " + signal.action.value + " " + str(signal.quantity) + " shares")

    def action(self, signal: Signal) -> Trade:
        if signal.action == SignalAction.BUY and self.buy_support(signal):
            self.add_position(signal)

        elif signal.action == SignalAction.SELL and self.sell_support(signal):
            self.sell_position(signal)
        else:
            trade = self.signal_to_trade(signal, invalid=True)
            return trade
            
        trade = self.signal_to_trade(signal)
        return trade

    def get_trading_days(self) -> list:
        trading_days = set()
        for portfolio_strategy in self.strategies.values():
            for row in portfolio_strategy.strategy.stock.data.itertuples(index=False):
                trading_days.add(row.date.date())

        return sorted(trading_days)

    def get_prices_for_date(self, current_date) -> dict[str, float]:
        prices = {}
        for portfolio_strategy in self.strategies.values():
            stock = portfolio_strategy.strategy.stock
            today_data = stock.data[stock.data["date"].dt.date == current_date]
            if today_data.empty:
                continue

            prices[stock.stock_name] = float(today_data.iloc[-1].close)

        return prices

    def record_daily_value(self, current_date, prices: dict[str, float]) -> None:
        self.latest_prices.update(prices)

        positions_value = 0.0
        for stock_name, quantity in self.positions.items():
            price = self.latest_prices.get(stock_name)
            if price is not None:
                positions_value += quantity * price

        total_value = self.cash + positions_value
        daily_value = {
            "date": current_date,
            "cash": self.cash,
            "positions_value": positions_value,
            "total_value": total_value,
        }
        self.daily_values.append(daily_value)
        return 

    def reset(self) -> None:
        self.positions= {}
        self.trades = []
        self.daily_values = []
        self.latest_prices = {}
        self.cash = self.initial_capital
        for portfolio_strategy in self.strategies.values():
            portfolio_strategy.reset_state()
        return 
    
    def run(self) -> pd.DataFrame | str:
        self.reset()
        if len(self.strategies) == 0:
            return "Please add at least one strategy"

        trading_days = self.get_trading_days()

        for current_date in trading_days:
            prices = self.get_prices_for_date(current_date)
            self.latest_prices.update(prices)

            for portfolio_strategy in self.strategies.values():
                today_signals = portfolio_strategy.generate_signal(current_date)
                for signal in today_signals:
                    trade = self.action(signal)
                    self.trades.append(trade)

            self.record_daily_value(current_date, prices)

        return self.generate_report_data

    @property
    def generate_report_data(self) -> pd.DataFrame:
        return pd.DataFrame(self.daily_values)

    def summary(self) -> dict:
        report_data = self.generate_report_data

        if report_data.empty:
            final_value = self.cash
            start_date = None
            end_date = None
        else:
            sorted_report = report_data.sort_values("date").reset_index(drop=True)
            final_value = float(sorted_report.iloc[-1]["total_value"])
            start_date = sorted_report.iloc[0]["date"]
            end_date = sorted_report.iloc[-1]["date"]

        total_pnl = final_value - self.initial_capital
        total_return = total_pnl / self.initial_capital if self.initial_capital else 0.0

        return {
            "initial_capital": self.initial_capital,
            "final_value": final_value,
            "total_pnl": total_pnl,
            "total_return": total_return,
            "trade_count": len(self.trades),
            "start_date": start_date,
            "end_date": end_date,
        }




            
