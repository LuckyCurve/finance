"""
该模块负责处理与交易详细数据相关的所有数据获取逻辑。
它封装了获取股票交易详情和现金交易详情的功能，
确保展示层与数据层分离。
"""

import pandas as pd

from adaptor.inbound.show_data import (
    get_currency_transaction_details,
    get_ticker_transaction_details,
)


def fetch_ticker_transaction_details() -> pd.DataFrame:
    """
    获取股票交易的详细数据。

    Returns:
        pd.DataFrame: 包含股票交易详情的DataFrame。
    """
    return get_ticker_transaction_details()


def fetch_currency_transaction_details() -> pd.DataFrame:
    """
    获取现金交易的详细数据。

    Returns:
        pd.DataFrame: 包含现金交易详情的DataFrame。
    """
    return get_currency_transaction_details()
