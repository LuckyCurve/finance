import json
import datetime
from decimal import Decimal

from db.entity import (
    Transaction,
    StockTransaction,
    CurrencyTransaction,
    TransactionType,
    AssetType,
    CurrencyType,
)


class TransactionIOService:
    @staticmethod
    def export_transactions(transactions: list[Transaction]) -> str:
        data = []
        for t in transactions:
            item = {
                "id": t.id,
                "date": t.date.isoformat(),
                "type": t.type.value,
                "trade_type": t.trade_type.value,
                "comment": t.comment,
                "ticker": None,
                "shares": None,
                "price": None,
                "currency": None,
                "currency_type": None,
            }
            if isinstance(t, StockTransaction):
                item.update(
                    {
                        "ticker": t.ticker,
                        "shares": str(t.shares) if t.shares is not None else None,
                        "price": str(t.price) if t.price is not None else None,
                    }
                )
            elif isinstance(t, CurrencyTransaction):
                item.update(
                    {
                        "currency": str(t.currency) if t.currency is not None else None,
                        "currency_type": t.currency_type.value
                        if t.currency_type is not None
                        else None,
                    }
                )
            data.append(item)
        return json.dumps(data, indent=4)

    @staticmethod
    def import_transactions(json_input: str) -> list[Transaction]:
        data = json.loads(json_input)
        transactions = []
        for item in data:
            trade_type = AssetType(item["trade_type"])
            if trade_type == AssetType.TICKER:
                transaction = StockTransaction(
                    date=datetime.date.fromisoformat(item["date"]),
                    type=TransactionType(item["type"]),
                    trade_type=trade_type,
                    ticker=item.get("ticker"),
                    shares=Decimal(item["shares"]) if item.get("shares") else None,
                    price=Decimal(item["price"]) if item.get("price") else None,
                    comment=item.get("comment"),
                )
            elif trade_type == AssetType.CURRENCY:
                transaction = CurrencyTransaction(
                    date=datetime.date.fromisoformat(item["date"]),
                    type=TransactionType(item["type"]),
                    trade_type=trade_type,
                    currency=Decimal(item["currency"])
                    if item.get("currency")
                    else None,
                    currency_type=CurrencyType(item["currency_type"])
                    if item.get("currency_type")
                    else None,
                    comment=item.get("comment"),
                )
            else:
                continue
            transactions.append(transaction)
        return transactions
