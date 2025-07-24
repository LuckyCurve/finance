"""
该模块负责处理与汇率相关的所有数据获取和计算逻辑。
它封装了获取最新汇率、历史汇率以及执行货币转换的功能，
确保展示层与数据层分离。
"""

from datetime import date

import pandas as pd

from adaptor.inbound.show_data import get_exchange_rate_details
from adaptor.outbound.currency import get_exchange_rate


def fetch_latest_exchange_rates() -> tuple[date, dict[str, float]]:
    """
    获取最新的汇率数据。

    Returns:
        Tuple[date, Dict[str, float]]:
            - current_date: 汇率数据的日期。
            - exchange_rates: 货币代码到汇率的映射字典 (1 USD = X Currency)。
    """
    # 获取今天的汇率数据
    current_date, exchange_rates_raw = get_exchange_rate(date.today())
    # 将汇率值转换为浮点数
    exchange_rates = {k: float(v) for k, v in exchange_rates_raw.items()}
    return current_date, exchange_rates


def fetch_historical_exchange_rates() -> pd.DataFrame:
    """
    获取历史汇率变化数据。

    Returns:
        pd.DataFrame: 包含历史汇率的DataFrame。
    """
    return get_exchange_rate_details()


def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str,
    exchange_rates: dict[str, float],
) -> float:
    """
    执行货币转换。

    Args:
        amount (float): 要转换的金额。
        from_currency (str): 原始货币代码。
        to_currency (str): 目标货币代码。
        exchange_rates (Dict[str, float]): 货币代码到汇率的映射字典 (1 USD = X Currency)。

    Returns:
        float: 转换后的金额。
    """
    if from_currency == to_currency:
        return amount
    elif from_currency == "USD":
        # 从USD转换为目标货币
        return amount * exchange_rates[to_currency]
    else:
        # 先将原始货币转换为USD，再从USD转换为目标货币
        amount_in_usd = amount / exchange_rates[from_currency]
        return amount_in_usd * exchange_rates[to_currency]
