"""
该模块负责为“当前财富看板”页面提供所有必要的数据。
它封装了数据获取、初步处理和货币转换的逻辑，
确保展示层与数据层分离。
"""

from typing import NamedTuple, Tuple

import pandas as pd

from adaptor.inbound.show_data import (
    get_current_account,
    get_current_ticker,
    get_exchange_rate_details,
)
from db.entity import AccountData, CurrencyType, TickerData
from pages.utils.common import convert_value
from service.calculate import calculate_ticker_daily_price


def fetch_initial_dashboard_data() -> (
    Tuple[AccountData, TickerData, pd.DataFrame, pd.DataFrame]
):
    """
    获取当前财富看板所需的初始数据。
    包括当前账户信息、当前股票信息、股票每日价格数据以及汇率详情。

    Returns:
        Tuple[AccountData, TickerData, pd.DataFrame, pd.DataFrame]:
            - current_account: 当前账户的NamedTuple数据
            - current_ticker: 当前股票的NamedTuple数据
            - ticker_daily_price_df: 包含股票每日价格的DataFrame
            - exchange_rates_df: 包含汇率详情的DataFrame
    """
    # 获取当前账户的财务数据
    current_account_tuple = get_current_account()
    # 获取当前股票的财务数据
    current_ticker_tuple = get_current_ticker()
    # 计算并获取股票每日价格数据
    ticker_daily_price_df = calculate_ticker_daily_price()
    # 获取所有货币的汇率详情
    exchange_rates_df = get_exchange_rate_details()

    # 将元组转换为NamedTuple
    current_account = AccountData(
        total_value=float(current_account_tuple[0]),
        yesterday_value=float(current_account_tuple[1]),
        currency_type=CurrencyType(current_account_tuple[2]),
        update_time=current_account_tuple[3],
    )
    current_ticker = TickerData(
        total_value=float(current_ticker_tuple[0]),
        yesterday_value=float(current_ticker_tuple[1]),
        currency_type=CurrencyType(current_ticker_tuple[2]),
        update_time=current_ticker_tuple[3],
    )

    return current_account, current_ticker, ticker_daily_price_df, exchange_rates_df


def _convert_financial_data_tuple(
    data_tuple: NamedTuple,  # Changed to NamedTuple
    selected_currency_type: CurrencyType,
    exchange_rates_df: pd.DataFrame,
    data_type: type,  # AccountData or TickerData
) -> NamedTuple:
    """
    辅助函数，用于转换财务数据元组为指定的数据类型（AccountData或TickerData）。
    """
    converted_value = convert_value(
        float(data_tuple.total_value),  # Access by attribute
        data_tuple.currency_type,  # Access by attribute
        selected_currency_type,
        exchange_rates_df,
    )
    converted_yesterday_value = convert_value(
        float(data_tuple.yesterday_value),  # Access by attribute
        data_tuple.currency_type,  # Access by attribute
        selected_currency_type,
        exchange_rates_df,
    )
    return data_type(
        total_value=converted_value,
        yesterday_value=converted_yesterday_value,
        currency_type=selected_currency_type,
        update_time=data_tuple.update_time,  # Access by attribute
    )


def get_converted_financial_data(
    current_account: AccountData,
    current_ticker: TickerData,
    selected_currency_type: CurrencyType,
    exchange_rates_df: pd.DataFrame,
) -> Tuple[AccountData, TickerData]:
    """
    根据选定的货币类型，转换账户和股票的财务数据。

    Args:
        current_account (AccountData): 原始当前账户数据。
        current_ticker (TickerData): 原始当前股票数据。
        selected_currency_type (CurrencyType): 用户选择的目标货币类型。
        exchange_rates_df (pd.DataFrame): 包含汇率详情的DataFrame。

    Returns:
        Tuple[AccountData, TickerData]:
            - converted_account: 转换后的账户数据。
            - converted_ticker: 转换后的股票数据。
    """
    # 转换账户数据
    converted_account = _convert_financial_data_tuple(
        current_account, selected_currency_type, exchange_rates_df, AccountData
    )

    # 转换股票数据
    converted_ticker = _convert_financial_data_tuple(
        current_ticker, selected_currency_type, exchange_rates_df, TickerData
    )

    return converted_account, converted_ticker
