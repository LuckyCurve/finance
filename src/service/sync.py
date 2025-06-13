# 执行对应的同步任务，将数据从外部数据源同步到数据库当中来


import datetime
from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, List

import pandas as pd
from sqlalchemy import asc, desc, func, select
from sqlalchemy.orm import Session
from yfinance import Ticker

import db
from db import engine
from db.entity import (
    Asset,
    Config,
    CurrencyType,
    ExchangedRate,
    StockAsset,
    StockTransaction,
    TickerInfo,
    Transaction,
    TransactionType,
)
from outbound import currency

LAST_SYNC_DATE = "last_sync_date"

DATE_FORMAT = "%Y-%m-%d"


def sync():
    with Session(db.engine) as session:
        sync_config = session.query(Config).filter(Config.key == LAST_SYNC_DATE).first()
        if sync_config is not None:
            sync_date = datetime.datetime.strptime(
                sync_config.value, DATE_FORMAT
            ).date()
            if sync_date >= date.today():
                print("检测到已经同步，跳过同步信息")
                return
        else:
            sync_config = Config(key=LAST_SYNC_DATE)

        sync_exchange_rate()
        sync_asset()
        sync_ticker_info()

        sync_config.value = date.today().strftime(DATE_FORMAT)
        if sync_config.id is None:
            session.add(sync_config)
        session.commit()


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

        current_assets: Dict[str, List[Decimal, Decimal]] = {}

        for d in pd.date_range(start=transactions[0].date, end=date.today()):
            d = d.date()
            if d in transactions_dict:
                for transaction in transactions_dict[d]:
                    transaction: StockTransaction

                    if transaction.ticker in current_assets:
                        history_shares, history_price = current_assets[
                            transaction.ticker
                        ]
                        if transaction.type == TransactionType.BUY:
                            history_price = (
                                history_shares * history_price
                                + transaction.price * transaction.shares
                            ) / (history_shares + transaction.shares)
                            history_shares = history_shares + transaction.shares
                        else:
                            history_price = (
                                history_shares * history_price
                                - transaction.price * transaction.shares
                            ) / (history_shares - transaction.shares)
                            history_shares = history_shares + transaction.shares
                        current_assets[transaction.ticker] = (
                            history_shares,
                            history_price,
                        )

                    elif transaction.type == TransactionType.BUY:
                        current_assets[transaction.ticker] = (
                            transaction.shares,
                            transaction.price,
                        )
                        pass
                    else:
                        raise Exception(
                            f"transaction 数据出现异常，当前持有资产为0依然进行出售操作，id: {transaction.id}"
                        )

            assets += [
                StockAsset(ticker=ticker, shares=shares, date=d, price=price)
                for ticker, (shares, price) in current_assets.items()
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


def sync_ticker_info():
    with Session(db.engine) as session:
        sql = select(StockTransaction.ticker, func.min(StockTransaction.date)).group_by(
            StockTransaction.ticker
        )

        session.query(TickerInfo).delete()

        for ticker_name, buy_date in session.execute(sql).all():
            ticker = Ticker(ticker_name)

            ticker_infos = []
            currency_type = CurrencyType(ticker.fast_info["currency"])
            for i, row in ticker.history(start=buy_date, end=date.today()).iterrows():
                ticker_infos.append(
                    TickerInfo(
                        date=i.date(),
                        ticker=ticker_name,
                        currency=Decimal(row["Close"]),
                        currency_type=currency_type,
                    )
                )
            session.add_all(ticker_infos)
            session.commit()
