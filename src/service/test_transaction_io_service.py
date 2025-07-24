import datetime
import json
from decimal import Decimal

from db.entity import (
    CurrencyTransaction,
    StockTransaction,
    TransactionType,
    AssetType,
    CurrencyType,
)
from service.transaction_io_service import TransactionIOService


def test_export_transactions():
    transactions = [
        StockTransaction(
            id=1,
            date=datetime.date(2023, 1, 1),
            type=TransactionType.BUY,
            trade_type=AssetType.TICKER,
            ticker="AAPL",
            shares=Decimal("10"),
            price=Decimal("150.0"),
            comment="Buy AAPL",
        ),
        CurrencyTransaction(
            id=2,
            date=datetime.date(2023, 1, 2),
            type=TransactionType.SELL,
            trade_type=AssetType.CURRENCY,
            currency=Decimal("1000.0"),
            currency_type=CurrencyType.USD,
            comment="Sell USD",
        ),
    ]

    json_output = TransactionIOService.export_transactions(transactions)

    expected_data = [
        {
            "id": 1,
            "date": "2023-01-01",
            "type": "buy",
            "trade_type": "ticker",
            "ticker": "AAPL",
            "shares": "10",
            "price": "150.0",
            "comment": "Buy AAPL",
            "currency": None,
            "currency_type": None,
        },
        {
            "id": 2,
            "date": "2023-01-02",
            "type": "sell",
            "trade_type": "currency",
            "ticker": None,
            "shares": None,
            "price": None,
            "comment": "Sell USD",
            "currency": "1000.0",
            "currency_type": "USD",
        },
    ]

    assert json.loads(json_output) == expected_data


def test_import_transactions():
    json_input = """
    [
        {
            "date": "2023-01-01",
            "type": "buy",
            "trade_type": "ticker",
            "ticker": "AAPL",
            "shares": "10",
            "price": "150.0",
            "comment": "Buy AAPL"
        },
        {
            "date": "2023-01-02",
            "type": "sell",
            "trade_type": "currency",
            "currency": "1000.0",
            "currency_type": "USD",
            "comment": "Sell USD"
        }
    ]
    """

    transactions = TransactionIOService.import_transactions(json_input)

    assert len(transactions) == 2

    assert isinstance(transactions[0], StockTransaction)
    assert transactions[0].date == datetime.date(2023, 1, 1)
    assert transactions[0].type == TransactionType.BUY
    assert transactions[0].trade_type == AssetType.TICKER
    assert transactions[0].ticker == "AAPL"
    assert transactions[0].shares == Decimal("10")
    assert transactions[0].price == Decimal("150.0")
    assert transactions[0].comment == "Buy AAPL"

    assert isinstance(transactions[1], CurrencyTransaction)
    assert transactions[1].date == datetime.date(2023, 1, 2)
    assert transactions[1].type == TransactionType.SELL
    assert transactions[1].trade_type == AssetType.CURRENCY
    assert transactions[1].currency == Decimal("1000.0")
    assert transactions[1].currency_type == CurrencyType.USD
    assert transactions[1].comment == "Sell USD"
