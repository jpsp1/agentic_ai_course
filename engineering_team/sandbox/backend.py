from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Optional


_DEFAULT_PRICES = {
    "AAPL": 100.0,
    "TSLA": 200.0,
    "GOOGL": 150.0,
}


def get_share_price(symbol: str) -> float:
    symbol = (symbol or "").strip().upper()
    if symbol in _DEFAULT_PRICES:
        return _DEFAULT_PRICES[symbol]
    raise LookupError(f"No price available for symbol: {symbol}")


@dataclass(frozen=True)
class Transaction:
    transaction_type: str
    timestamp: datetime
    symbol: Optional[str] = None
    quantity: Optional[int] = None
    cash_amount: Optional[float] = None
    share_price: Optional[float] = None
    total_value: Optional[float] = None
    notes: Optional[str] = None


class TradingAccount:
    def __init__(self, account_id: str, owner_name: str, price_lookup: Callable[[str], float] | None = None) -> None:
        self.account_id = account_id.strip()
        self.owner_name = owner_name.strip()
        self.cash_balance = 0.0
        self.initial_deposit_total = 0.0
        self.holdings: dict[str, int] = {}
        self.transactions: list[Transaction] = []
        self._price_lookup = price_lookup or get_share_price

    def record_account_creation(self) -> None:
        self._append_transaction("create_account", notes="Account created")

    def deposit(self, amount: float) -> None:
        self._validate_positive_amount(amount)
        self.cash_balance += float(amount)
        self.initial_deposit_total += float(amount)
        self._append_transaction("deposit", cash_amount=float(amount), total_value=self.cash_balance)

    def withdraw(self, amount: float) -> None:
        self._validate_positive_amount(amount)
        amount = float(amount)
        if amount > self.cash_balance:
            raise ValueError("Insufficient cash balance")
        self.cash_balance -= amount
        self._append_transaction("withdraw", cash_amount=amount, total_value=self.cash_balance)

    def buy_shares(self, symbol: str, quantity: int) -> None:
        symbol = self._normalize_symbol(symbol)
        self._validate_positive_quantity(quantity)
        price = self._price_for_symbol(symbol)
        total_cost = quantity * price
        if total_cost > self.cash_balance:
            raise ValueError("Insufficient cash to buy shares")
        self.cash_balance -= total_cost
        self.holdings[symbol] = self.holdings.get(symbol, 0) + quantity
        self._append_transaction(
            "buy",
            symbol=symbol,
            quantity=quantity,
            share_price=price,
            cash_amount=total_cost,
            total_value=self.cash_balance,
        )

    def sell_shares(self, symbol: str, quantity: int) -> None:
        symbol = self._normalize_symbol(symbol)
        self._validate_positive_quantity(quantity)
        owned = self.holdings.get(symbol, 0)
        if quantity > owned:
            raise ValueError("Insufficient holdings to sell shares")
        price = self._price_for_symbol(symbol)
        total_value = quantity * price
        self.cash_balance += total_value
        remaining = owned - quantity
        if remaining:
            self.holdings[symbol] = remaining
        else:
            self.holdings.pop(symbol, None)
        self._append_transaction(
            "sell",
            symbol=symbol,
            quantity=quantity,
            share_price=price,
            cash_amount=total_value,
            total_value=self.cash_balance,
        )

    def get_holdings(self) -> dict[str, int]:
        return dict(self.holdings)

    def get_portfolio_value(self) -> float:
        value = self.cash_balance
        for symbol, qty in self.holdings.items():
            value += qty * self._price_for_symbol(symbol)
        return value

    def get_profit_loss(self) -> float:
        return self.get_portfolio_value() - self.initial_deposit_total

    def get_transactions(self) -> list[Transaction]:
        return list(self.transactions)

    def get_summary(self) -> dict[str, object]:
        return {
            "account_id": self.account_id,
            "owner_name": self.owner_name,
            "cash_balance": self.cash_balance,
            "initial_deposit_total": self.initial_deposit_total,
            "holdings": self.get_holdings(),
            "portfolio_value": self.get_portfolio_value(),
            "profit_loss": self.get_profit_loss(),
            "transaction_count": len(self.transactions),
        }

    def _validate_positive_amount(self, amount: float) -> None:
        if amount is None or float(amount) <= 0:
            raise ValueError("Amount must be positive")

    def _validate_positive_quantity(self, quantity: int) -> None:
        if quantity is None or int(quantity) <= 0:
            raise ValueError("Quantity must be positive")

    def _append_transaction(
        self,
        transaction_type: str,
        symbol: str | None = None,
        quantity: int | None = None,
        cash_amount: float | None = None,
        share_price: float | None = None,
        total_value: float | None = None,
        notes: str | None = None,
    ) -> None:
        self.transactions.append(
            Transaction(
                transaction_type=transaction_type,
                timestamp=datetime.utcnow(),
                symbol=symbol,
                quantity=quantity,
                cash_amount=cash_amount,
                share_price=share_price,
                total_value=total_value,
                notes=notes,
            )
        )

    def _price_for_symbol(self, symbol: str) -> float:
        price = self._price_lookup(symbol)
        if price is None:
            raise LookupError(f"No price available for symbol: {symbol}")
        return float(price)

    @staticmethod
    def _normalize_symbol(symbol: str) -> str:
        symbol = (symbol or "").strip().upper()
        if not symbol:
            raise ValueError("Symbol must be provided")
        return symbol
