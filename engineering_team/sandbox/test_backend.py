import unittest
from datetime import datetime

from backend import Transaction, TradingAccount


def fake_price_lookup(symbol: str) -> float:
    prices = {"AAPL": 100.0, "TSLA": 200.0, "GOOGL": 150.0}
    symbol = (symbol or "").upper()
    if symbol not in prices:
        raise LookupError(symbol)
    return prices[symbol]


def make_account() -> TradingAccount:
    account = TradingAccount("acct-1", "Alice", price_lookup=fake_price_lookup)
    account.record_account_creation()
    return account


class TestTradingAccount(unittest.TestCase):
    def test_account_creation_records_transaction(self):
        account = make_account()
        self.assertEqual(account.account_id, "acct-1")
        self.assertEqual(account.owner_name, "Alice")
        self.assertEqual(account.cash_balance, 0.0)
        self.assertEqual(account.initial_deposit_total, 0.0)
        self.assertEqual(account.get_holdings(), {})
        txs = account.get_transactions()
        self.assertEqual(len(txs), 1)
        self.assertEqual(txs[0].transaction_type, "create_account")
        self.assertEqual(txs[0].notes, "Account created")
        self.assertIsInstance(txs[0].timestamp, datetime)

    def test_deposit_increases_balances_and_records_transaction(self):
        account = make_account()
        account.deposit(1000)
        self.assertEqual(account.cash_balance, 1000.0)
        self.assertEqual(account.initial_deposit_total, 1000.0)
        tx = account.get_transactions()[-1]
        self.assertEqual(tx.transaction_type, "deposit")
        self.assertEqual(tx.cash_amount, 1000.0)
        self.assertEqual(tx.total_value, 1000.0)

    def test_deposit_rejects_invalid(self):
        account = make_account()
        for amount in (0, -1, None):
            with self.subTest(amount=amount):
                with self.assertRaises(ValueError):
                    account.deposit(amount)

    def test_withdrawal_decreases_balance_and_records_transaction(self):
        account = make_account()
        account.deposit(1000)
        account.withdraw(250)
        self.assertEqual(account.cash_balance, 750.0)
        tx = account.get_transactions()[-1]
        self.assertEqual(tx.transaction_type, "withdraw")
        self.assertEqual(tx.cash_amount, 250.0)
        self.assertEqual(tx.total_value, 750.0)

    def test_withdrawal_rejects_invalid_and_insufficient_funds(self):
        account = make_account()
        account.deposit(100)
        for amount in (0, -1, None, 101):
            with self.subTest(amount=amount):
                with self.assertRaises(ValueError):
                    account.withdraw(amount)

    def test_buy_shares_updates_holdings_cash_and_records_transaction(self):
        account = make_account()
        account.deposit(1000)
        account.buy_shares("AAPL", 3)
        self.assertEqual(account.get_holdings(), {"AAPL": 3})
        self.assertEqual(account.cash_balance, 700.0)
        tx = account.get_transactions()[-1]
        self.assertEqual(tx.transaction_type, "buy")
        self.assertEqual(tx.symbol, "AAPL")
        self.assertEqual(tx.quantity, 3)
        self.assertEqual(tx.share_price, 100.0)
        self.assertEqual(tx.cash_amount, 300.0)
        self.assertEqual(tx.total_value, 700.0)

    def test_buy_rejects_invalid_quantity_insufficient_cash_and_unknown_symbol(self):
        account = make_account()
        account.deposit(1000)
        for qty in (0, -1, None):
            with self.subTest(qty=qty):
                with self.assertRaises(ValueError):
                    account.buy_shares("AAPL", qty)
        with self.assertRaises(ValueError):
            account.buy_shares("AAPL", 20)
        with self.assertRaises(LookupError):
            account.buy_shares("MSFT", 1)

    def test_sell_shares_updates_holdings_cash_and_removes_symbol_when_zero(self):
        account = make_account()
        account.deposit(1000)
        account.buy_shares("AAPL", 3)
        account.sell_shares("AAPL", 2)
        self.assertEqual(account.get_holdings(), {"AAPL": 1})
        self.assertEqual(account.cash_balance, 900.0)
        account.sell_shares("AAPL", 1)
        self.assertEqual(account.get_holdings(), {})
        self.assertEqual(account.cash_balance, 1000.0)
        tx = account.get_transactions()[-1]
        self.assertEqual(tx.transaction_type, "sell")
        self.assertEqual(tx.symbol, "AAPL")
        self.assertEqual(tx.quantity, 1)
        self.assertEqual(tx.share_price, 100.0)
        self.assertEqual(tx.cash_amount, 100.0)
        self.assertEqual(tx.total_value, 1000.0)

    def test_sell_rejects_invalid_quantity_insufficient_holdings_and_unknown_symbol(self):
        account = make_account()
        account.deposit(1000)
        account.buy_shares("AAPL", 1)
        for qty in (0, -1, None):
            with self.subTest(qty=qty):
                with self.assertRaises(ValueError):
                    account.sell_shares("AAPL", qty)
        with self.assertRaises(ValueError):
            account.sell_shares("AAPL", 2)
        with self.assertRaises(LookupError):
            account.sell_shares("MSFT", 1)

    def test_portfolio_value_and_profit_loss(self):
        account = make_account()
        account.deposit(1000)
        account.buy_shares("AAPL", 2)
        self.assertEqual(account.get_portfolio_value(), 1000.0)
        self.assertEqual(account.get_profit_loss(), 0.0)
        account.sell_shares("AAPL", 1)
        self.assertEqual(account.get_portfolio_value(), 1000.0)
        self.assertEqual(account.get_profit_loss(), 0.0)

    def test_holdings_are_copied(self):
        account = make_account()
        account.deposit(1000)
        account.buy_shares("AAPL", 1)
        holdings = account.get_holdings()
        holdings["AAPL"] = 999
        self.assertEqual(account.get_holdings(), {"AAPL": 1})

    def test_transactions_are_copied_and_ordered(self):
        account = make_account()
        account.deposit(100)
        account.withdraw(50)
        txs = account.get_transactions()
        self.assertEqual([t.transaction_type for t in txs], ["create_account", "deposit", "withdraw"])
        txs.append("x")
        self.assertEqual(len(account.get_transactions()), 3)

    def test_multiple_symbols_and_summary(self):
        account = make_account()
        account.deposit(2000)
        account.buy_shares("AAPL", 2)
        account.buy_shares("TSLA", 1)
        self.assertEqual(account.get_holdings(), {"AAPL": 2, "TSLA": 1})
        self.assertEqual(account.get_portfolio_value(), 2000.0)
        summary = account.get_summary()
        self.assertEqual(summary["account_id"], "acct-1")
        self.assertEqual(summary["owner_name"], "Alice")
        self.assertEqual(summary["cash_balance"], 1400.0)
        self.assertEqual(summary["initial_deposit_total"], 2000.0)
        self.assertEqual(summary["holdings"], {"AAPL": 2, "TSLA": 1})
        self.assertEqual(summary["portfolio_value"], 2000.0)
        self.assertEqual(summary["profit_loss"], 0.0)
        self.assertEqual(summary["transaction_count"], 4)

    def test_transaction_dataclass_fields(self):
        tx = Transaction("deposit", datetime.utcnow(), cash_amount=1.0)
        self.assertEqual(tx.transaction_type, "deposit")
        self.assertEqual(tx.cash_amount, 1.0)


if __name__ == "__main__":
    unittest.main()
