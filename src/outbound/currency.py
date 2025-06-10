from datetime import date
from decimal import Decimal
from typing import Dict

from curl_cffi import requests

from db.entity import CurrencyType


def get_currency(time: date) -> Dict[str, Decimal]:
    """获取 USD 兑其他货币的汇率数据

    Args:
        datetime (datetime): 获取汇率的时间

    Returns:
        Dict[str, Decimal]: {货币类型, 汇率}
    """
    url = f"https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@{time.strftime('%Y-%m-%d')}/v1/currencies/usd.json"
    response = requests.get(url, impersonate="chrome")
    exchanged_rate: Dict[str, float] = response.json()["usd"]

    return {
        currency.upper(): Decimal(rate)
        for currency, rate in exchanged_rate.items()
        if currency.upper() in CurrencyType
    }


if __name__ == "__main__":
    print(get_currency(date.today()))
