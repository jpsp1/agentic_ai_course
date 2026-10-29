from __future__ import annotations

import gradio as gr

from backend import TradingAccount


PALETTE = {
    "gold": "#ecad0a",
    "blue": "#209dd7",
    "purple": "#753991",
    "bg": "#f7f8fb",
    "bg_dark": "#111827",
    "surface": "#ffffff",
    "surface_dark": "#1f2937",
    "text": "#111827",
    "text_dark": "#f9fafb",
    "muted": "#6b7280",
    "muted_dark": "#9ca3af",
}


THEME_CSS = f"""
:root {{
    --gold: {PALETTE['gold']};
    --blue: {PALETTE['blue']};
    --purple: {PALETTE['purple']};
    --app-bg: {PALETTE['bg']};
    --app-surface: {PALETTE['surface']};
    --app-text: {PALETTE['text']};
    --app-muted: {PALETTE['muted']};
}}

@media (prefers-color-scheme: dark) {{
    :root {{
        --app-bg: {PALETTE['bg_dark']};
        --app-surface: {PALETTE['surface_dark']};
        --app-text: {PALETTE['text_dark']};
        --app-muted: {PALETTE['muted_dark']};
    }}
}}

.gradio-container {{
    background: linear-gradient(180deg, var(--app-bg), color-mix(in srgb, var(--app-bg) 88%, var(--blue) 12%));
    color: var(--app-text);
}}

#hero-banner {{
    border: 1px solid color-mix(in srgb, var(--gold) 40%, transparent);
    background:
        radial-gradient(circle at top right, color-mix(in srgb, var(--purple) 18%, transparent), transparent 36%),
        linear-gradient(135deg, color-mix(in srgb, var(--blue) 14%, var(--app-surface)) 0%, color-mix(in srgb, var(--gold) 10%, var(--app-surface)) 100%);
    border-radius: 22px;
    padding: 1.25rem 1.4rem;
    box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
}}

#hero-banner h1 {{
    margin: 0;
    font-size: 2rem;
    line-height: 1.1;
}}

#hero-banner p {{
    margin: 0.35rem 0 0;
    color: var(--app-muted);
}}

.section-card {{
    border: 1px solid color-mix(in srgb, var(--blue) 18%, var(--app-surface));
    background: var(--app-surface);
    border-radius: 18px;
    padding: 1rem;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
}}

.section-title {{
    margin: 0 0 0.75rem;
    font-weight: 700;
    color: var(--app-text);
}}

.small-muted {{
    color: var(--app-muted);
    font-size: 0.92rem;
}}

.gr-button {{
    border-radius: 999px !important;
    border: none !important;
    font-weight: 700 !important;
}}

button.primary {{
    background: linear-gradient(135deg, var(--blue), var(--purple)) !important;
    color: white !important;
}}

button.secondary {{
    background: linear-gradient(135deg, var(--gold), color-mix(in srgb, var(--gold) 70%, white)) !important;
    color: #111827 !important;
}}

#status-success, #status-error, #status-info {{
    border-radius: 14px;
    padding: 0.8rem 1rem;
}}

#status-success {{
    background: color-mix(in srgb, var(--blue) 10%, var(--app-surface));
    border: 1px solid color-mix(in srgb, var(--blue) 25%, transparent);
}}

#status-error {{
    background: color-mix(in srgb, #ef4444 10%, var(--app-surface));
    border: 1px solid color-mix(in srgb, #ef4444 28%, transparent);
}}

#status-info {{
    background: color-mix(in srgb, var(--gold) 10%, var(--app-surface));
    border: 1px solid color-mix(in srgb, var(--gold) 28%, transparent);
}}

.gr-dataframe, .gr-json {{
    border-radius: 16px !important;
    overflow: hidden;
}}
"""


def _money(value: float) -> str:
    return f"${value:,.2f}"


def _empty_holdings_table():
    return [["No holdings", 0]]


def _empty_transactions_table():
    return [["No transactions", "", "", "", "", "", ""]]


def _holdings_table(account: TradingAccount | None):
    if not account:
        return _empty_holdings_table()
    holdings = account.get_holdings()
    if not holdings:
        return _empty_holdings_table()
    return [[symbol, qty] for symbol, qty in sorted(holdings.items())]


def _transactions_table(account: TradingAccount | None):
    if not account:
        return _empty_transactions_table()
    rows = []
    for tx in account.get_transactions():
        rows.append([
            tx.timestamp.isoformat(sep=" ", timespec="seconds"),
            tx.transaction_type,
            tx.symbol or "",
            tx.quantity if tx.quantity is not None else "",
            _money(tx.cash_amount) if tx.cash_amount is not None else "",
            _money(tx.share_price) if tx.share_price is not None else "",
            _money(tx.total_value) if tx.total_value is not None else "",
        ])
    return rows or _empty_transactions_table()


def _summary_markdown(account: TradingAccount | None) -> str:
    if not account:
        return (
            "### Account summary\n\n"
            "No account yet. Create one to start tracking deposits, trades, and portfolio performance."
        )
    s = account.get_summary()
    return (
        "### Account summary\n\n"
        f"- **Account ID:** `{s['account_id']}`\n"
        f"- **Owner:** {s['owner_name']}\n"
        f"- **Cash balance:** {_money(s['cash_balance'])}\n"
        f"- **Initial deposits:** {_money(s['initial_deposit_total'])}\n"
        f"- **Portfolio value:** {_money(s['portfolio_value'])}\n"
        f"- **Profit / Loss:** {_money(s['profit_loss'])}\n"
        f"- **Transactions:** {s['transaction_count']}"
    )


def _status_box(message: str, kind: str = "info") -> str:
    box_id = {
        "success": "status-success",
        "error": "status-error",
        "info": "status-info",
    }.get(kind, "status-info")
    return f'<div id="{box_id}">{message}</div>'


def handle_create_account(owner_name: str, account_id: str):
    owner_name = (owner_name or "").strip() or "Single User"
    account_id = (account_id or "").strip() or "acct-001"
    account = TradingAccount(account_id=account_id, owner_name=owner_name)
    account.record_account_creation()
    return account, _status_box(f"Created account <strong>{account.account_id}</strong> for <strong>{account.owner_name}</strong>.", "success"), _summary_markdown(account), _holdings_table(account), _transactions_table(account)


def handle_deposit(account: TradingAccount | None, amount: float):
    if account is None:
        return None, _status_box("Create an account before depositing funds.", "error"), _summary_markdown(None), _holdings_table(None), _transactions_table(None)
    try:
        account.deposit(amount)
        return account, _status_box(f"Deposited {_money(float(amount))}. Cash balance is now {_money(account.cash_balance)}.", "success"), _summary_markdown(account), _holdings_table(account), _transactions_table(account)
    except Exception as exc:
        return account, _status_box(f"Deposit failed: {exc}", "error"), _summary_markdown(account), _holdings_table(account), _transactions_table(account)


def handle_withdraw(account: TradingAccount | None, amount: float):
    if account is None:
        return None, _status_box("Create an account before withdrawing funds.", "error"), _summary_markdown(None), _holdings_table(None), _transactions_table(None)
    try:
        account.withdraw(amount)
        return account, _status_box(f"Withdrew {_money(float(amount))}. Cash balance is now {_money(account.cash_balance)}.", "success"), _summary_markdown(account), _holdings_table(account), _transactions_table(account)
    except Exception as exc:
        return account, _status_box(f"Withdrawal failed: {exc}", "error"), _summary_markdown(account), _holdings_table(account), _transactions_table(account)


def handle_buy(account: TradingAccount | None, symbol: str, quantity: int):
    if account is None:
        return None, _status_box("Create an account before buying shares.", "error"), _summary_markdown(None), _holdings_table(None), _transactions_table(None)
    try:
        account.buy_shares(symbol, quantity)
        return account, _status_box(f"Bought {int(quantity)} shares of {symbol.strip().upper()}.", "success"), _summary_markdown(account), _holdings_table(account), _transactions_table(account)
    except Exception as exc:
        return account, _status_box(f"Buy order failed: {exc}", "error"), _summary_markdown(account), _holdings_table(account), _transactions_table(account)


def handle_sell(account: TradingAccount | None, symbol: str, quantity: int):
    if account is None:
        return None, _status_box("Create an account before selling shares.", "error"), _summary_markdown(None), _holdings_table(None), _transactions_table(None)
    try:
        account.sell_shares(symbol, quantity)
        return account, _status_box(f"Sold {int(quantity)} shares of {symbol.strip().upper()}.", "success"), _summary_markdown(account), _holdings_table(account), _transactions_table(account)
    except Exception as exc:
        return account, _status_box(f"Sell order failed: {exc}", "error"), _summary_markdown(account), _holdings_table(account), _transactions_table(account)


def handle_refresh_report(account: TradingAccount | None):
    return _summary_markdown(account), _holdings_table(account), _transactions_table(account)


def build_app():
    with gr.Blocks(css=THEME_CSS, title="Trading Simulation Account Manager") as demo:
        gr.Markdown(
            """
            <div id="hero-banner">
              <h1>Trading Simulation Account Manager</h1>
              <p>Deposit funds, place buy/sell orders, and review balances, holdings, profit/loss, and transaction history.</p>
            </div>
            """
        )

        account_state = gr.State(None)

        with gr.Row():
            with gr.Column(scale=4):
                with gr.Group(elem_classes=["section-card"]):
                    gr.Markdown("### Account setup", elem_classes=["section-title"])
                    gr.Markdown("Create the single simulated account for this demo.", elem_classes=["small-muted"])
                    with gr.Row():
                        owner_name_input = gr.Textbox(label="Owner name", value="Single User", placeholder="Alice")
                        account_id_input = gr.Textbox(label="Account ID", value="acct-001", placeholder="acct-001")
                    create_account_button = gr.Button("Create account", variant="primary", elem_classes=["primary"])
                    account_status_output = gr.HTML(value=_status_box("No account created yet.", "info"))

            with gr.Column(scale=5):
                with gr.Group(elem_classes=["section-card"]):
                    gr.Markdown("### Cash actions", elem_classes=["section-title"])
                    gr.Markdown("Manage the account cash balance safely.", elem_classes=["small-muted"])
                    with gr.Row():
                        amount_input = gr.Number(label="Amount", value=0.0, precision=2)
                        deposit_button = gr.Button("Deposit", variant="secondary", elem_classes=["secondary"])
                        withdraw_button = gr.Button("Withdraw", variant="secondary", elem_classes=["secondary"])
                    cash_status_output = gr.HTML(value=_status_box("Deposits and withdrawals will appear here.", "info"))

        with gr.Row():
            with gr.Column(scale=5):
                with gr.Group(elem_classes=["section-card"]):
                    gr.Markdown("### Trade actions", elem_classes=["section-title"])
                    gr.Markdown("Use the built-in share pricing: AAPL, TSLA, and GOOGL.", elem_classes=["small-muted"])
                    with gr.Row():
                        symbol_input = gr.Textbox(label="Symbol", value="AAPL", placeholder="AAPL")
                        quantity_input = gr.Number(label="Quantity", value=1, precision=0)
                    with gr.Row():
                        buy_button = gr.Button("Buy shares", variant="primary", elem_classes=["primary"])
                        sell_button = gr.Button("Sell shares", variant="primary", elem_classes=["primary"])
                    trade_status_output = gr.HTML(value=_status_box("Trade responses will appear here.", "info"))

            with gr.Column(scale=4):
                with gr.Group(elem_classes=["section-card"]):
                    gr.Markdown("### Current holdings", elem_classes=["section-title"])
                    gr.Markdown("Your positions update after every trade.", elem_classes=["small-muted"])
                    holdings_output = gr.Dataframe(
                        headers=["Symbol", "Quantity"],
                        value=_empty_holdings_table(),
                        interactive=False,
                        wrap=True,
                    )

        with gr.Row():
            with gr.Column(scale=5):
                with gr.Group(elem_classes=["section-card"]):
                    gr.Markdown("### Reports", elem_classes=["section-title"])
                    gr.Markdown("Review the account summary and current performance.", elem_classes=["small-muted"])
                    refresh_report_button = gr.Button("Refresh report", variant="secondary", elem_classes=["secondary"])
                    summary_output = gr.Markdown(value=_summary_markdown(None))

            with gr.Column(scale=4):
                with gr.Group(elem_classes=["section-card"]):
                    gr.Markdown("### Transaction history", elem_classes=["section-title"])
                    gr.Markdown("Chronological audit trail of account activity.", elem_classes=["small-muted"])
                    refresh_transactions_button = gr.Button("Refresh transactions", variant="secondary", elem_classes=["secondary"])
                    transactions_output = gr.Dataframe(
                        headers=["Timestamp", "Type", "Symbol", "Quantity", "Cash Amount", "Share Price", "Total Value"],
                        value=_empty_transactions_table(),
                        interactive=False,
                        wrap=True,
                    )

        create_account_button.click(
            fn=handle_create_account,
            inputs=[owner_name_input, account_id_input],
            outputs=[account_state, account_status_output, summary_output, holdings_output, transactions_output],
        )
        deposit_button.click(
            fn=handle_deposit,
            inputs=[account_state, amount_input],
            outputs=[account_state, cash_status_output, summary_output, holdings_output, transactions_output],
        )
        withdraw_button.click(
            fn=handle_withdraw,
            inputs=[account_state, amount_input],
            outputs=[account_state, cash_status_output, summary_output, holdings_output, transactions_output],
        )
        buy_button.click(
            fn=handle_buy,
            inputs=[account_state, symbol_input, quantity_input],
            outputs=[account_state, trade_status_output, summary_output, holdings_output, transactions_output],
        )
        sell_button.click(
            fn=handle_sell,
            inputs=[account_state, symbol_input, quantity_input],
            outputs=[account_state, trade_status_output, summary_output, holdings_output, transactions_output],
        )
        refresh_report_button.click(
            fn=handle_refresh_report,
            inputs=[account_state],
            outputs=[summary_output, holdings_output, transactions_output],
        )
        refresh_transactions_button.click(
            fn=lambda account: _transactions_table(account),
            inputs=[account_state],
            outputs=[transactions_output],
        )

    return demo


def main() -> None:
    demo = build_app()
    demo.launch(share=True)


if __name__ == "__main__":
    main()
