"""
This module contains functions for creating metric components for the Streamlit application.
"""

import streamlit
from adaptor.inbound.show_data import format_decimal


from db.entity import AccountData, TickerData


def display_finance_metrics(
    converted_account: AccountData,
    converted_ticker: TickerData,
    selected_currency_symbol: str,
):
    """
    Displays the main financial metrics in columns.

    Args:
        converted_account (tuple): A tuple containing converted account data.
        converted_ticker (tuple): A tuple containing converted ticker data.
        selected_currency_symbol (str): The symbol of the selected currency.
    """
    col1, col2 = streamlit.columns(2)
    with col1:
        streamlit.metric(
            label=f"我的财富总值 {converted_account.update_time}",
            value=f"{format_decimal(converted_account.total_value)} {selected_currency_symbol}",
            delta=f"{format_decimal(converted_account.total_value - converted_account.yesterday_value)}",
        )
    with col2:
        streamlit.metric(
            label=f"我的股市数据 {converted_ticker.update_time}",
            value=f"{format_decimal(converted_ticker.total_value)} {selected_currency_symbol}",
            delta=f"{format_decimal(converted_ticker.total_value - converted_ticker.yesterday_value)}",
        )
