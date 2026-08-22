from __future__ import annotations

import json
import os
from datetime import date, timedelta
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import pandas as pd
import streamlit as st


API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

trade_columns = [
    "trade_date",
    "side",
    "stock_name",
    "quantity",
    "price"]


def post_json(path: str, payload: dict) -> dict:
    # Send JSON input from the Streamlit UI to the FastAPI backend.
    request = Request(
        f"{API_BASE_URL}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def get_json(path: str) -> dict:
    # Read JSON output from a FastAPI GET endpoint.
    with urlopen(f"{API_BASE_URL}{path}", timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def build_strategy_config(
    name: str,
    condition_type: str,
    trigger_price: float,
    comparison: str,
    gap: int,
    action: str,
    sizing_type: str,
    unit: float,
    rule_start_date: date,
    rule_end_date: date,
) -> dict:
    # Convert form inputs into the strategy config expected by StrategyFactory.
    if condition_type == "price":
        condition = {
            "type": "price",
            "trigger_price": trigger_price,
            "comparison": comparison,
        }
    else:
        condition = {
            "type": "date_gap",
            "gap": gap,
        }

    return {
        "name": name,
        "condition": condition,
        "action": action,
        "sizing": {
            "type": sizing_type,
            "unit": unit,
        },
        "start_date": rule_start_date.isoformat(),
        "end_date": rule_end_date.isoformat(),
    }


def render_rule_inputs(rule_label: str, action: str, default_name: str, key_prefix: str) -> dict | None:
    # Render one trading rule and return a config dictionary when the rule is enabled.
    is_enabled = st.checkbox(rule_label, value=action == "BUY", key=f"{key_prefix}_enabled")
    if not is_enabled:
        return None

    strategy_name = st.text_input("Rule Name", value=default_name, key=f"{key_prefix}_name")

    condition_col, sizing_col, date_col = st.columns(3)
    with condition_col:
        condition_type = st.selectbox(
            "Condition",
            options=["price", "date_gap"],
            key=f"{key_prefix}_condition_type",
        )
        if condition_type == "price":
            trigger_price = st.number_input(
                "Trigger Price",
                min_value=0.01,
                value=100.0,
                key=f"{key_prefix}_trigger_price",
            )
            comparison = st.selectbox(
                "Comparison",
                options=["below_or_equal", "above_or_equal"],
                index=0 if action == "BUY" else 1,
                key=f"{key_prefix}_comparison",
            )
            gap = 1
        else:
            gap = st.number_input("Gap Days", min_value=1, value=5, step=1, key=f"{key_prefix}_gap")
            trigger_price = 100.0
            comparison = "below_or_equal"

    with sizing_col:
        if action == "BUY":
            sizing_type = st.selectbox(
                "Sizing",
                options=["fixed_shares", "cash_percent"],
                key=f"{key_prefix}_sizing_type",
            )
        else:
            sizing_type = st.selectbox(
                "Sizing",
                options=["fixed_shares", "position_percent"],
                key=f"{key_prefix}_sizing_type",
            )

        if sizing_type == "fixed_shares":
            unit = st.number_input("Unit", min_value=1, value=1, step=1, key=f"{key_prefix}_unit")
        else:
            unit = st.number_input(
                "Unit",
                min_value=0.01,
                max_value=1.0,
                value=0.5,
                key=f"{key_prefix}_unit",
            )

    with date_col:
        rule_start_date = st.date_input("Rule Start Date", value=start_date, key=f"{key_prefix}_start")
        rule_end_date = st.date_input("Rule End Date", value=end_date, key=f"{key_prefix}_end")

    return build_strategy_config(
        name=strategy_name,
        condition_type=condition_type,
        trigger_price=trigger_price,
        comparison=comparison,
        gap=int(gap),
        action=action,
        sizing_type=sizing_type,
        unit=unit,
        rule_start_date=rule_start_date,
        rule_end_date=rule_end_date,
    )


st.set_page_config(page_title="Investment Strategy Lab", layout="wide")

st.title("Investment Strategy Lab")

st.subheader("1. Initial Capital")
initial_capital = st.number_input(
    "Initial Capital",
    min_value=100.0,
    value=10000.0,
    step=500.0,
)

st.subheader("2. Stock")
stock_col, date_col_1, date_col_2 = st.columns(3)
with stock_col:
    ticker = st.text_input("Ticker", value="AAPL").strip().upper()
with date_col_1:
    start_date = st.date_input("Start Date", value=date.today() - timedelta(days=90))
with date_col_2:
    end_date = st.date_input("End Date", value=date.today())

st.subheader("3. Trading Rules")
buy_rule_config = render_rule_inputs("Add Buy Rule", "BUY", "buy_rule", "buy")
sell_rule_config = render_rule_inputs("Add Sell Rule", "SELL", "sell_rule", "sell")

run_clicked = st.button("Run Backtest", type="primary")

if run_clicked:
    if not ticker:
        st.error("Ticker is required.")
    elif start_date >= end_date:
        st.error("Start Date must be before End Date.")
    else:
        strategy_configs = [
            strategy_config
            for strategy_config in [buy_rule_config, sell_rule_config]
            if strategy_config is not None
        ]

        if not strategy_configs:
            st.error("Please add at least one trading rule.")
            st.stop()

        payload = {
            "ticker": ticker,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "initial_capital": initial_capital,
            "data_type": "daily",
            "strategies": strategy_configs,
        }

        try:
            prices = get_json(
                f"/api/prices?stock_name={ticker}&start={start_date.isoformat()}&end={end_date.isoformat()}&data_type=daily"
            )
            result = post_json("/api/backtest", payload)
        except HTTPError as exc:
            error_body = exc.read().decode("utf-8")
            st.error(f"Backend returned an error: {error_body}")
        except URLError:
            st.error("FastAPI backend is not running. Start it with: uvicorn app.main:app --reload")
        else:
            price_df = pd.DataFrame(prices["prices"])
            daily_value_df = pd.DataFrame(result["daily_values"])

            chart_col_1, chart_col_2 = st.columns(2)
            with chart_col_1:
                st.subheader("Stock Price")
                st.line_chart(price_df, x="date", y="close")

            with chart_col_2:
                st.subheader("Portfolio Value")
                st.line_chart(daily_value_df, x="date", y="total_value")

            
            summary = result["summary"]

            metric_col_1, metric_col_2, metric_col_3, metric_col_4 = st.columns(4)

            with metric_col_1:
                st.metric("Initial Capital", f'${summary["initial_capital"]:,.2f}')

            with metric_col_2:
                st.metric("Final Value", f'${summary["final_value"]:,.2f}')

            with metric_col_3:
                st.metric("Total Return", f'{summary["total_return"]:.2%}')

            with metric_col_4:
                st.metric("PnL", f'${summary["total_pnl"]:,.2f}')
                        
            trade_df = pd.DataFrame(result["trades"])
            if not trade_df.empty:
                visible_columns = [column for column in trade_columns if column in trade_df.columns]

                with st.expander("Trade History", expanded=False):
                    st.dataframe(trade_df[visible_columns], use_container_width=True)
            else:
                st.info("No trades were generated for this backtest.")

st.caption("More features are still under development.")
