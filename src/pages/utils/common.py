"""
This module contains common utility functions shared across different pages of the Streamlit application.
"""

import pandas as pd
from pyecharts.commons.utils import JsCode

from adaptor.inbound.show_data import CurrencyType


def get_pie_tooltip_formatter(total_assets: float) -> JsCode:
    """
    Generates a JavaScript function for formatting tooltips in Pyecharts pie charts.

    This formatter displays the series name, the formatted value, and the percentage
    of the total assets.

    Args:
        total_assets (float): The total value of assets to calculate the percentage against.

    Returns:
        JsCode: A JavaScript function string to be used in Pyecharts tooltip options.
    """
    return JsCode(
        f"""
        function (params) {{
            var total_assets = {total_assets};
            var formatted_value = new Intl.NumberFormat('en-US', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }}).format(params.value);
            var percentage = ((params.value / total_assets) * 100).toFixed(2);
            return params.marker + '<b>' + params.name + '</b><br/>' + formatted_value + ' (' + percentage + '%)';
        }}
        """
    )


def convert_value(
    value: float,
    original_currency_type: CurrencyType,
    target_currency_type: CurrencyType,
    exchange_rates: pd.DataFrame,
) -> float:
    """
    Converts a financial value from its original currency to a target currency using provided exchange rates.

    Args:
        value (float): The financial value to convert.
        original_currency_type (CurrencyType): The original currency type of the value.
        target_currency_type (CurrencyType): The desired target currency type.
        exchange_rates (pd.DataFrame): DataFrame containing exchange rates, with columns "货币类型" and "汇率".

    Returns:
        float: The converted value in the target currency.
    """
    if original_currency_type == target_currency_type:
        return value

    # Convert original to USD first if it's not USD
    if original_currency_type != CurrencyType.USD:
        original_rate_row = exchange_rates[
            exchange_rates["货币类型"] == original_currency_type.value
        ]
        if not original_rate_row.empty:
            original_rate = original_rate_row["汇率"].iloc[0]
            value_in_usd = value / original_rate
        else:
            value_in_usd = value  # Assume 1:1 if rate not found
    else:
        value_in_usd = value

    # Convert from USD to target currency
    if target_currency_type != CurrencyType.USD:
        target_rate_row = exchange_rates[
            exchange_rates["货币类型"] == target_currency_type.value
        ]
        if not target_rate_row.empty:
            target_rate = target_rate_row["汇率"].iloc[0]
            return value_in_usd * target_rate
        else:
            return value_in_usd  # Assume 1:1 if rate not found
    else:
        return value_in_usd
