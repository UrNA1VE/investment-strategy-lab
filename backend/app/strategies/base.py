from abc import ABC, abstractmethod
from typing import Any


class BaseStrategy(ABC):
    strategy_name: str

    def __init__(self, parameters: dict[str, Any] | None = None) -> None:
        self.parameters = parameters or {}

    @abstractmethod
    def generate_signals(self, price_data: Any) -> Any:
        raise NotImplementedError
