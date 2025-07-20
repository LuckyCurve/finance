"""
This module contains functions for creating metric components for the Streamlit application.
"""

import streamlit
from adaptor.inbound.show_data import format_decimal


def display_finance_metrics(
    converted_account: tuple, converted_ticker: tuple, selected_currency_symbol: str
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
            label=f"我的财富总值 {converted_account[3]}",
            value=f"{format_decimal(converted_account[0])} {selected_currency_symbol}",
            delta=f"{format_decimal(converted_account[0] - converted_account[1])}",
        )
    with col2:
        streamlit.metric(
            label=f"我的股市数据 {converted_ticker[3]}",
            value=f"{format_decimal(converted_ticker[0])} {selected_currency_symbol}",
            delta=f"{format_decimal(converted_ticker[0] - converted_ticker[1])}",
        )
