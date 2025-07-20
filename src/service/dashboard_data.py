"""
该模块负责为“当前财富看板”页面提供所有必要的数据。
它封装了数据获取、初步处理和货币转换的逻辑，
确保展示层与数据层分离。
"""

from typing import Tuple

import pandas as pd

from adaptor.inbound.show_data import (
    CurrencyType,
    get_current_account,
    get_current_ticker,
    get_exchange_rate_details,
)
from pages.utils.common import convert_value
from service.calculate import calculate_ticker_daily_price


def fetch_initial_dashboard_data() -> Tuple[Tuple, Tuple, pd.DataFrame, pd.DataFrame]:
    """
    获取当前财富看板所需的初始数据。
    包括当前账户信息、当前股票信息、股票每日价格数据以及汇率详情。

    Returns:
        Tuple[Tuple, Tuple, pd.DataFrame, pd.DataFrame]:
            - current_account: 当前账户的元组数据 (例如: (总资产, 昨日总资产, 货币类型, 更新时间))
            - current_ticker: 当前股票的元组数据 (例如: (股票总市值, 昨日股票总市值, 货币类型, 更新时间))
            - ticker_daily_price_df: 包含股票每日价格的DataFrame
            - exchange_rates_df: 包含汇率详情的DataFrame
    """
    # 获取当前账户的财务数据
    current_account = get_current_account()
    # 获取当前股票的财务数据
    current_ticker = get_current_ticker()
    # 计算并获取股票每日价格数据
    ticker_daily_price_df = calculate_ticker_daily_price()
    # 获取所有货币的汇率详情
    exchange_rates_df = get_exchange_rate_details()
    return current_account, current_ticker, ticker_daily_price_df, exchange_rates_df


def get_converted_financial_data(
    current_account: Tuple,
    current_ticker: Tuple,
    selected_currency_type: CurrencyType,
    exchange_rates_df: pd.DataFrame,
) -> Tuple[Tuple, Tuple]:
    """
    根据选定的货币类型，转换账户和股票的财务数据。

    Args:
        current_account (Tuple): 原始当前账户数据。
        current_ticker (Tuple): 原始当前股票数据。
        selected_currency_type (CurrencyType): 用户选择的目标货币类型。
        exchange_rates_df (pd.DataFrame): 包含汇率详情的DataFrame。

    Returns:
        Tuple[Tuple, Tuple]:
            - converted_account: 转换后的账户数据。
            - converted_ticker: 转换后的股票数据。
    """
    # 转换账户总资产
    converted_account_value = convert_value(
        float(current_account[0]),
        current_account[2],
        selected_currency_type,
        exchange_rates_df,
    )
    # 转换账户昨日总资产
    converted_account_yesterday_value = convert_value(
        float(current_account[1]),
        current_account[2],
        selected_currency_type,
        exchange_rates_df,
    )
    # 构建转换后的账户数据元组
    converted_account = (
        converted_account_value,
        converted_account_yesterday_value,
        selected_currency_type,
        current_account[3],
    )

    # 转换股票总市值
    converted_ticker_value = convert_value(
        float(current_ticker[0]),
        current_ticker[2],
        selected_currency_type,
        exchange_rates_df,
    )
    # 转换股票昨日总市值
    converted_ticker_yesterday_value = convert_value(
        float(current_ticker[1]),
        current_ticker[2],
        selected_currency_type,
        exchange_rates_df,
    )
    # 构建转换后的股票数据元组
    converted_ticker = (
        converted_ticker_value,
        converted_ticker_yesterday_value,
        selected_currency_type,
        current_ticker[3],
    )

    return converted_account, converted_ticker
