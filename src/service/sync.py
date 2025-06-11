# 执行对应的同步任务，将数据从外部数据源同步到数据库当中来


from datetime import date, timedelta
from decimal import Decimal
from turtle import pd

import pandas as pd
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from db import engine
from db.entity import (
    Asset,
    ExchangedRate,
    StockAsset,
    StockTransaction,
    Transaction,
    TransactionType,
)
from outbound import currency


def sync_asset():
    with Session(engine) as session:
        session.query(Asset).delete()
        transactions = session.query(Transaction).order_by(asc(Transaction.date)).all()
        if not transactions:
            print("交易记录为空，无法生成资产数据")
            return
        transactions_dict = {}
        for transaction in transactions:
            if transaction.date in transactions_dict:
                transactions_dict[transaction.date].append(transaction)
            else:
                transactions_dict[transaction.date] = [transaction]

        assets = []

        current_assets = {}

        for d in pd.date_range(start=transactions[0].date, end=date.today()):
            d = d.date()
            if d in transactions_dict:
                for transaction in transactions_dict[d]:
                    transaction: StockTransaction
                    number = Decimal(0)
                    if transaction.ticker in current_assets:
                        number = current_assets[transaction.ticker]
                    if transaction.type == TransactionType.BUY:
                        number += transaction.shares
                    else:
                        number -= transaction.shares
                    current_assets[transaction.ticker] = number

            assets += [
                StockAsset(ticker=ticker, shares=shares, date=d)
                for ticker, shares in current_assets.items()
            ]

        session.add_all(assets)
        session.commit()


def sync_exchange_rate() -> None:
    with Session(engine) as session:
        count = session.query(ExchangedRate).count()
        if count == 0:
            cloest_date = (
                session.query(Transaction).order_by(desc(Transaction.date)).first().date
            )
            days = [
                cloest_date + timedelta(days=x)
                for x in range(0, (date.today() - cloest_date).days + 1)
            ]

            res = []
            for day in days:
                res += [
                    ExchangedRate(currency_type=currency_type, rate=rate, date=day)
                    for currency_type, rate in currency.get_currency(day).items()
                ]
            session.add_all(res)
        else:
            cloest_date = (
                session.query(ExchangedRate)
                .order_by(desc(ExchangedRate.date))
                .first()
                .date
            )
            days = [
                cloest_date + timedelta(days=x)
                for x in range(1, (date.today() - cloest_date).days + 1)
            ]

            res = []
            for day in days:
                res += [
                    ExchangedRate(currency_type=currency_type, rate=rate, date=day)
                    for currency_type, rate in currency.get_currency(day).items()
                ]
            session.add_all(res)

        session.commit()
