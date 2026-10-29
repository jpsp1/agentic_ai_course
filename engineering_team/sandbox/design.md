# Design: Trading Simulation Account Management System

## 1. Overview

Build a simple single-process Python application that manages a simulated trading account. The system will:

- create a user account
- accept cash deposits and withdrawals
- record stock buy/sell trades with quantities
- compute current portfolio value using `get_share_price(symbol)`
- compute profit/loss relative to initial deposits
- report holdings, portfolio value, profit/loss, and transaction history
- prevent invalid withdrawals, over-buying, and selling shares not owned

The application will be split into:

- **backend module**: core account and portfolio logic
- **frontend module**: Gradio 6 UI
- **test module**: unit tests for backend behavior

All files live in the same directory. No subdirectories or packages.

---

## 2. Files to Create

1. `backend.py`
2. `app.py`
3. `test_backend.py`

Optional helper file if desired, but not required:
- `share_prices.py` only if the team wants to isolate price lookup; otherwise keep `get_share_price` in `backend.py` or inject it into the backend class.

---

## 3. Domain Model

### Key concepts

- **Account**: represents one user’s simulated trading account
- **Cash balance**: liquid funds available for withdrawals and share purchases
- **Holdings**: quantity of each stock symbol owned
- **Transactions**: audit trail of deposits, withdrawals, buys, and sells
- **Initial deposit total**: sum of all deposits, used for profit/loss reference

### Important business rules

- Deposits increase cash balance and increase initial deposit total
- Withdrawals decrease cash balance only if sufficient funds exist
- Buy orders reduce cash balance by `quantity * current_price` only if sufficient funds exist
- Sell orders increase cash balance by `quantity * current_price` only if holdings are sufficient
- Portfolio value = cash balance + market value of all holdings
- Profit/loss = portfolio value - initial deposit total
- Holdings report should include current quantities per symbol
- Transaction history should preserve chronological order

---

## 4. Backend Design

## 4.1 Module: `backend.py`

### Responsibilities

- define the account state and all validation rules
- expose methods for account operations and reporting
- use `get_share_price(symbol)` to value shares

### External dependency

The backend must call:

```python
def get_share_price(symbol: str) -> float:
    ...
```

For tests, a fixed-price implementation must be provided or injected.

---

## 4.2 Data Structures

### `Transaction`
Represent a single account event.

Fields:
- `transaction_type: str`  
  One of: `"create_account"`, `"deposit"`, `"withdraw"`, `"buy"`, `"sell"`
- `timestamp: datetime`
- `symbol: str | None`
- `quantity: int | None`
- `cash_amount: float | None`
- `share_price: float | None`
- `total_value: float | None`
- `notes: str | None`

Recommended as a dataclass, but not required by this design.

---

## 4.3 Class: `TradingAccount`

### Purpose
Encapsulates the account state and business logic.

### State
- `account_id: str`
- `owner_name: str`
- `cash_balance: float`
- `initial_deposit_total: float`
- `holdings: dict[str, int]`
- `transactions: list[Transaction]`

### Constructor signature

```python
class TradingAccount:
    def __init__(self, account_id: str, owner_name: str) -> None:
        ...
```

### Methods

#### Account creation / initialization record

```python
def record_account_creation(self) -> None:
    ...
```

Adds a `"create_account"` transaction.

---

#### Deposit funds

```python
def deposit(self, amount: float) -> None:
    ...
```

Validation:
- amount must be positive

Effects:
- increases `cash_balance`
- increases `initial_deposit_total`
- records a `"deposit"` transaction

Raises:
- `ValueError` on non-positive amount

---

#### Withdraw funds

```python
def withdraw(self, amount: float) -> None:
    ...
```

Validation:
- amount must be positive
- amount must not exceed cash balance

Effects:
- decreases `cash_balance`
- records a `"withdraw"` transaction

Raises:
- `ValueError` on invalid amount or insufficient funds

---

#### Buy shares

```python
def buy_shares(self, symbol: str, quantity: int) -> None:
    ...
```

Validation:
- symbol must be non-empty
- quantity must be positive
- total cost must not exceed cash balance
- current share price must be available via `get_share_price(symbol)`

Effects:
- decreases `cash_balance` by `quantity * price`
- increases holdings for `symbol`
- records a `"buy"` transaction

Raises:
- `ValueError` if quantity invalid
- `LookupError` or `ValueError` if symbol price unavailable
- `ValueError` if insufficient cash

---

#### Sell shares

```python
def sell_shares(self, symbol: str, quantity: int) -> None:
    ...
```

Validation:
- symbol must be non-empty
- quantity must be positive
- holdings must contain enough shares of symbol
- current share price must be available via `get_share_price(symbol)`

Effects:
- increases `cash_balance` by `quantity * price`
- decreases holdings for `symbol`
- removes symbol from holdings if quantity becomes zero
- records a `"sell"` transaction

Raises:
- `ValueError` if quantity invalid or insufficient holdings
- `LookupError` or `ValueError` if symbol price unavailable

---

#### Current holdings report

```python
def get_holdings(self) -> dict[str, int]:
    ...
```

Returns a copy of the holdings dictionary.

---

#### Current portfolio value

```python
def get_portfolio_value(self) -> float:
    ...
```

Returns:
- `cash_balance + sum(quantity * current_price for each held symbol)`

---

#### Profit or loss

```python
def get_profit_loss(self) -> float:
    ...
```

Returns:
- `get_portfolio_value() - initial_deposit_total`

---

#### Transaction history

```python
def get_transactions(self) -> list[Transaction]:
    ...
```

Returns a copy of transactions in chronological order.

---

#### Account summary

```python
def get_summary(self) -> dict[str, object]:
    ...
```

Returns a structured summary for the UI:
- account_id
- owner_name
- cash_balance
- initial_deposit_total
- holdings
- portfolio_value
- profit_loss
- transaction_count

---

## 4.4 Helper Functions in `backend.py`

### Price lookup adapter

To keep tests deterministic, price lookup should be injectable.

Recommended helper signatures:

```python
def get_share_price(symbol: str) -> float:
    ...
```

If using dependency injection, the class can instead accept a callable:

```python
def __init__(
    self,
    account_id: str,
    owner_name: str,
    price_lookup: callable | None = None,
) -> None:
    ...
```

Recommended design choice:
- keep `price_lookup` as an injected callable defaulting to `get_share_price`
- this simplifies testing

If the team chooses that approach, internal helper signatures should include:

```python
def _get_price(self, symbol: str) -> float:
    ...
```

---

## 4.5 Suggested Internal Validation Helpers

These are implementation details, but the design should include them for clarity.

```python
def _validate_positive_amount(self, amount: float) -> None:
    ...
```

```python
def _validate_positive_quantity(self, quantity: int) -> None:
    ...
```

```python
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
    ...
```

```python
def _price_for_symbol(self, symbol: str) -> float:
    ...
```

---

## 5. Frontend Design

## 5.1 Module: `app.py`

### Responsibilities

- render a Gradio 6 interface
- create and manage a `TradingAccount` object
- allow the user to perform actions
- display account summary, holdings, transactions, and errors

---

## 5.2 Gradio 6 API Guidance

The frontend engineer should follow these Gradio 6 patterns:

### Core app container
Use:

```python
with gr.Blocks() as demo:
    ...
```

### Layout components
Use:
- `gr.Row()`
- `gr.Column()`
- `gr.Group()` if desired

### Common components
Use:
- `gr.Textbox(...)`
- `gr.Number(...)`
- `gr.Button(...)`
- `gr.Markdown(...)`
- `gr.Dataframe(...)`
- `gr.JSON(...)` if useful for structured output

### Event methods
Use Gradio component event methods such as:
- `.click(...)`
- `.change(...)`
- `.submit(...)`
- `.load(...)`

The app should wire buttons with `.click(...)` and should update outputs through returned values.

### Important Gradio 6 notes
- Prefer `with gr.Blocks() as demo:` over older global-style app creation
- Return output values directly from event handlers; do not mutate UI objects manually
- For table-like display, `gr.Dataframe` should be used with values passed as plain row/column data
- Keep event handler functions pure and deterministic where possible

---

## 5.3 UI Structure

### Top-level sections

1. **Account setup**
2. **Cash actions**
3. **Trade actions**
4. **Reports**
5. **Transaction history**
6. **Status / error display**

---

## 5.4 Suggested UI Components

### Account setup section

Inputs:
- `owner_name_input: gr.Textbox`
- `account_id_input: gr.Textbox`

Buttons:
- `create_account_button: gr.Button`

Outputs:
- `account_status_output: gr.Markdown`

---

### Deposit / withdrawal section

Inputs:
- `amount_input: gr.Number`

Buttons:
- `deposit_button: gr.Button`
- `withdraw_button: gr.Button`

Outputs:
- `cash_status_output: gr.Markdown`
- `error_output: gr.Markdown`

---

### Buy / sell section

Inputs:
- `symbol_input: gr.Textbox`
- `quantity_input: gr.Number`

Buttons:
- `buy_button: gr.Button`
- `sell_button: gr.Button`

Outputs:
- `trade_status_output: gr.Markdown`
- `holdings_output: gr.Dataframe` or `gr.JSON`

---

### Reports section

Buttons:
- `refresh_report_button: gr.Button`

Outputs:
- `summary_output: gr.JSON` or `gr.Markdown`
- `portfolio_value_output: gr.Markdown`
- `profit_loss_output: gr.Markdown`

---

### Transaction history section

Outputs:
- `transactions_output: gr.Dataframe`

Button:
- `refresh_transactions_button: gr.Button`

---

## 5.5 Frontend Function Signatures

The frontend should define helper functions that convert backend state to UI-friendly outputs.

### State creation helper

```python
def create_account(owner_name: str, account_id: str) -> tuple[str, object]:
    ...
```

Recommended return:
- a status message
- a fresh `TradingAccount` instance or a stored state token

If using `gr.State`, prefer explicit state passing.

---

### UI event handlers

```python
def handle_create_account(owner_name: str, account_id: str) -> tuple[object, str]:
    ...
```

```python
def handle_deposit(account: TradingAccount | None, amount: float) -> tuple[TradingAccount | None, str, str]:
    ...
```

```python
def handle_withdraw(account: TradingAccount | None, amount: float) -> tuple[TradingAccount | None, str, str]:
    ...
```

```python
def handle_buy(account: TradingAccount | None, symbol: str, quantity: int) -> tuple[TradingAccount | None, str, object, str]:
    ...
```

```python
def handle_sell(account: TradingAccount | None, symbol: str, quantity: int) -> tuple[TradingAccount | None, str, object, str]:
    ...
```

```python
def handle_refresh_report(account: TradingAccount | None) -> tuple[object, str, str, object]:
    ...
```

```python
def handle_refresh_transactions(account: TradingAccount | None) -> object:
    ...
```

---

## 5.6 Suggested Gradio State Handling

Use one `gr.State` object to store the current `TradingAccount`.

Example design intent:
- `account_state: gr.State`
- all mutating actions take `account_state` as input and return updated `account_state`

### State usage pattern
- if no account exists, return a helpful message
- once created, pass the account object through event chains

---

## 5.7 Gradio Event Wiring Plan

### Create account button
```python
create_account_button.click(
    fn=handle_create_account,
    inputs=[owner_name_input, account_id_input],
    outputs=[account_state, account_status_output],
)
```

### Deposit button
```python
deposit_button.click(
    fn=handle_deposit,
    inputs=[account_state, amount_input],
    outputs=[account_state, cash_status_output, error_output],
)
```

### Withdraw button
```python
withdraw_button.click(
    fn=handle_withdraw,
    inputs=[account_state, amount_input],
    outputs=[account_state, cash_status_output, error_output],
)
```

### Buy button
```python
buy_button.click(
    fn=handle_buy,
    inputs=[account_state, symbol_input, quantity_input],
    outputs=[account_state, trade_status_output, holdings_output, error_output],
)
```

### Sell button
```python
sell_button.click(
    fn=handle_sell,
    inputs=[account_state, symbol_input, quantity_input],
    outputs=[account_state, trade_status_output, holdings_output, error_output],
)
```

### Refresh reports button
```python
refresh_report_button.click(
    fn=handle_refresh_report,
    inputs=[account_state],
    outputs=[summary_output, portfolio_value_output, profit_loss_output, holdings_output],
)
```

### Refresh transactions button
```python
refresh_transactions_button.click(
    fn=handle_refresh_transactions,
    inputs=[account_state],
    outputs=[transactions_output],
)
```

---

## 6. Backend Implementation Notes for Engineer

## 6.1 `backend_engineer` task list

### Implement:
- `Transaction` structure
- `TradingAccount` class
- `get_share_price(symbol)` integration point
- validation logic
- reporting methods
- deterministic summary output for UI

### Must ensure:
- no negative cash balance after withdrawals or buys
- no over-selling
- no negative or zero deposits/withdrawals/trades
- transactions are recorded for all successful actions
- transaction order is preserved
- holdings never go negative

### Internal formatting:
- keep numeric values consistently rounded for display if needed, but preserve raw values in calculations
- return copies from getter methods to avoid external mutation

---

## 7. Frontend Implementation Notes for Engineer

## 7.1 `frontend_engineer` task list

### Implement:
- Gradio app in `app.py`
- account state persistence via `gr.State`
- form inputs and output displays
- action buttons and event wiring
- user-friendly success/error messages
- reporting panels for holdings, summary, and transaction history

### UI behavior requirements:
- clear error messages when user tries invalid actions
- no crash on empty or missing account state
- reports update immediately after successful actions
- transaction history should be readable in tabular form

### Gradio 6 guidance:
- use `gr.Blocks`
- use modern component constructors with keyword arguments
- use event callbacks with `.click`
- return values matching declared outputs exactly
- use `gr.State` for the account object
- prefer `gr.Dataframe` or `gr.JSON` for structured outputs

---

## 8. Test Design

## 8.1 Module: `test_backend.py`

### Responsibilities
- validate all backend behavior
- cover success cases and failure cases
- ensure deterministic behavior using a fixed-price share lookup

### Test setup
Use a mock/fake price lookup function returning fixed prices such as:
- `AAPL -> 100.0`
- `TSLA -> 200.0`
- `GOOGL -> 150.0`

### Test helper signatures

```python
def fake_price_lookup(symbol: str) -> float:
    ...
```

```python
def make_account() -> TradingAccount:
    ...
```

---

## 8.2 Test cases to implement

### Account creation
- creates account with zero cash and no holdings
- records create transaction

### Deposits
- deposit increases cash balance
- deposit increases initial deposit total
- deposit rejects zero/negative values

### Withdrawals
- withdrawal decreases cash balance
- withdrawal rejects zero/negative values
- withdrawal rejects amount greater than cash balance

### Buy shares
- buying shares reduces cash
- buying shares increases holdings
- buying shares records transaction
- buying rejects zero/negative quantity
- buying rejects insufficient cash
- buying with unknown symbol fails

### Sell shares
- selling shares increases cash
- selling shares decreases holdings
- selling all shares removes symbol from holdings
- selling rejects zero/negative quantity
- selling rejects more than owned
- selling with unknown symbol fails if price lookup fails

### Portfolio value
- portfolio value equals cash plus market value of holdings

### Profit/loss
- profit/loss equals portfolio value minus initial deposits

### Holdings
- holdings report returns expected quantities
- returned holdings are a copy, not a live reference

### Transactions
- transactions are returned in order
- transaction list includes successful events only
- returned transaction list is a copy

### Edge behaviors
- multiple symbols are handled correctly
- sequential buy/sell operations update balances correctly

---

## 9. Suggested Function and Class Signatures Summary

## 9.1 `backend.py`

```python
def get_share_price(symbol: str) -> float:
    ...
```

```python
class Transaction:
    ...
```

```python
class TradingAccount:
    def __init__(self, account_id: str, owner_name: str) -> None:
        ...

    def record_account_creation(self) -> None:
        ...

    def deposit(self, amount: float) -> None:
        ...

    def withdraw(self, amount: float) -> None:
        ...

    def buy_shares(self, symbol: str, quantity: int) -> None:
        ...

    def sell_shares(self, symbol: str, quantity: int) -> None:
        ...

    def get_holdings(self) -> dict[str, int]:
        ...

    def get_portfolio_value(self) -> float:
        ...

    def get_profit_loss(self) -> float:
        ...

    def get_transactions(self) -> list[Transaction]:
        ...

    def get_summary(self) -> dict[str, object]:
        ...
```

Optional helpers:

```python
def _validate_positive_amount(self, amount: float) -> None:
    ...
```

```python
def _validate_positive_quantity(self, quantity: int) -> None:
    ...
```

```python
def _append_transaction(...) -> None:
    ...
```

---

## 9.2 `app.py`

```python
def handle_create_account(owner_name: str, account_id: str) -> tuple[object, str]:
    ...
```

```python
def handle_deposit(account: TradingAccount | None, amount: float) -> tuple[TradingAccount | None, str, str]:
    ...
```

```python
def handle_withdraw(account: TradingAccount | None, amount: float) -> tuple[TradingAccount | None, str, str]:
    ...
```

```python
def handle_buy(account: TradingAccount | None, symbol: str, quantity: int) -> tuple[TradingAccount | None, str, object, str]:
    ...
```

```python
def handle_sell(account: TradingAccount | None, symbol: str, quantity: int) -> tuple[TradingAccount | None, str, object, str]:
    ...
```

```python
def handle_refresh_report(account: TradingAccount | None) -> tuple[object, str, str, object]:
    ...
```

```python
def handle_refresh_transactions(account: TradingAccount | None) -> object:
    ...
```

```python
def build_app() -> object:
    ...
```

```python
def main() -> None:
    ...
```

---

## 9.3 `test_backend.py`

```python
def fake_price_lookup(symbol: str) -> float:
    ...
```

```python
def make_account() -> TradingAccount:
    ...
```

Test functions should be written for each scenario listed above.

---

## 10. Assignment Plan

## backend_engineer
Own `backend.py`.

### Deliverables
- `TradingAccount` class
- `Transaction` model
- fixed share price integration point
- all validation and reporting logic
- clean, testable API surface

### Acceptance criteria
- all business rules enforced
- all methods return expected values
- no UI dependencies in backend
- support deterministic testing via injected price lookup or stable test helper

---

## frontend_engineer
Own `app.py`.

### Deliverables
- Gradio 6 app
- account state management
- event handlers
- output formatting
- user-friendly interaction flow

### Acceptance criteria
- app launches successfully
- all actions work end-to-end
- errors are displayed gracefully
- summaries, holdings, and transactions render correctly

---

## test_engineer
Own `test_backend.py`.

### Deliverables
- unit test coverage for all backend behavior
- deterministic fake price lookup
- tests for success and failure cases

### Acceptance criteria
- tests verify all stated business rules
- tests run independently and deterministically
- tests cover edge cases and error handling

---

## 11. Recommended Integration Flow

1. backend engineer implements `TradingAccount`
2. test engineer writes tests against backend API
3. frontend engineer builds Gradio interface on top of backend
4. integrate and verify:
   - create account
   - deposit
   - buy shares
   - sell shares
   - withdraw cash
   - inspect holdings / P&L / transactions

---

## 12. Final Notes

- Keep the backend pure and UI-agnostic.
- Keep the frontend thin: no trading logic should live in Gradio handlers.
- Ensure all calculations use the backend as the single source of truth.
- Use deterministic fake pricing in tests.
- Do not create subdirectories; place all files in the same directory.