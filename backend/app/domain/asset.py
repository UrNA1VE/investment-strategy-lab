from dataclasses import dataclass


@dataclass(frozen=True)
class Asset:
    symbol: str
    asset_type: str = "stock"
    currency: str = "USD"

    def normalized_symbol(self) -> str:
        return self.symbol.strip().upper()
