"""
该模块负责处理与股票买入和现金平账相关的业务逻辑。
它封装了对底层服务（如 `buy_stock` 和 `adjust_currency`）的调用，
并包含必要的输入验证逻辑，确保交易操作的正确性。
"""

import datetime
from typing import Tuple

from db.entity import CurrencyType
from service.adjust import adjust_currency
from service.transaction import buy_stock


def process_stock_purchase(
    symbol: str, trans_date: datetime.date, shares: float, price: float
) -> Tuple[bool, str]:
    """
    处理股票买入操作。

    Args:
        symbol (str): 股票代码。
        trans_date (datetime.date): 交易日期。
        shares (float): 买入数量。
        price (float): 买入价格。

    Returns:
        Tuple[bool, str]:
            - bool: 操作是否成功。
            - str: 操作结果消息（成功或失败原因）。
    """
    if not symbol.strip():
        return False, "股票代码不能为空"
    if shares <= 0 or price <= 0:
        return False, "买入数量和价格必须大于零"
    try:
        buy_stock(symbol, trans_date, shares, price)
        return True, "股票买入记录已添加"
    except Exception as e:
        return False, f"操作失败: {str(e)}"


def process_currency_adjustment(
    final_amount: float, currency_type: CurrencyType
) -> Tuple[bool, str]:
    """
    处理现金平账操作。

    Args:
        final_amount (float): 调整后总额。
        currency_type (CurrencyType): 币种。

    Returns:
        Tuple[bool, str]:
            - bool: 操作是否成功。
            - str: 操作结果消息（成功或失败原因）。
    """
    try:
        adjust_currency(final_amount, currency_type)
        return True, "现金平账操作已完成"
    except Exception as e:
        return False, f"操作失败: {str(e)}"
