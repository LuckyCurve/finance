"""
This Streamlit application provides a comprehensive financial dashboard,
displaying current wealth, stock data, asset allocation, and transaction details.
It includes functionality to switch between different currency views for wealth and stock metrics.
"""

from typing import Tuple

import pandas as pd
import streamlit

from adaptor.inbound.show_data import (
    CurrencyType,
    get_current_account,
    get_current_ticker,
    get_exchange_rate_details,
)
from pages.components.charts import (
    create_daily_change_line_chart,
    create_stock_earn_rate_line_chart,
    create_stock_market_bar_chart,
    create_sunburst_chart,
    create_total_assets_line_chart,
)
from pages.components.metrics import display_finance_metrics
from pages.utils.common import convert_value
from service.calculate import calculate_ticker_daily_price


def _get_initial_data() -> Tuple[Tuple, Tuple, pd.DataFrame]:
    """Fetches initial account, ticker, and daily price data."""
    current_account = get_current_account()
    current_ticker = get_current_ticker()
    ticker_daily_price_df = calculate_ticker_daily_price()
    return current_account, current_ticker, ticker_daily_price_df


def _handle_currency_selection_and_conversion(
    current_account: Tuple, current_ticker: Tuple, exchange_rates_df: pd.DataFrame
) -> Tuple[Tuple, Tuple, str]:
    """Handles currency selection and converts account/ticker values."""
    all_currencies = [currency.value for currency in CurrencyType]

    selected_currency_symbol = streamlit.selectbox(
        "选择显示货币",
        options=all_currencies,
    )
    selected_currency_type = CurrencyType(selected_currency_symbol)

    converted_account_value = convert_value(
        float(current_account[0]),
        current_account[2],
        selected_currency_type,
        exchange_rates_df,
    )
    converted_account_yesterday_value = convert_value(
        float(current_account[1]),
        current_account[2],
        selected_currency_type,
        exchange_rates_df,
    )
    converted_account = (
        converted_account_value,
        converted_account_yesterday_value,
        selected_currency_type,
        current_account[3],
    )

    converted_ticker_value = convert_value(
        float(current_ticker[0]),
        current_ticker[2],
        selected_currency_type,
        exchange_rates_df,
    )
    converted_ticker_yesterday_value = convert_value(
        float(current_ticker[1]),
        current_ticker[2],
        selected_currency_type,
        exchange_rates_df,
    )
    converted_ticker = (
        converted_ticker_value,
        converted_ticker_yesterday_value,
        selected_currency_type,
        current_ticker[3],
    )

    return (
        converted_account,
        converted_ticker,
        selected_currency_symbol,
    )


def current_finance_summary() -> None:
    """Main function to display the current finance summary dashboard."""
    streamlit.title(":rainbow[我的财富看板]")

    current_account, current_ticker, ticker_daily_price_df = _get_initial_data()
    exchange_rates = get_exchange_rate_details()

    (
        converted_account,
        converted_ticker,
        selected_currency_symbol,
    ) = _handle_currency_selection_and_conversion(
        current_account, current_ticker, exchange_rates
    )

    display_finance_metrics(
        converted_account, converted_ticker, selected_currency_symbol
    )

    streamlit.write("\n")

    create_sunburst_chart(current_ticker[0], ticker_daily_price_df)
    create_total_assets_line_chart()
    create_stock_market_bar_chart(ticker_daily_price_df)
    create_stock_earn_rate_line_chart()
    create_daily_change_line_chart()


if __name__ == "__main__":
    streamlit.set_page_config(
        page_title="当前财富看板",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    current_finance_summary()
