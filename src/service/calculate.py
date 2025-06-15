from datetime import date, timedelta
from decimal import Decimal

import pandas as pd
from sqlalchemy import asc
from sqlalchemy.orm import Session

import db
from db.entity import Account, CurrencyType, ExchangedRate, StockAsset
from service.ticker import get_ticker_close_price


def calculate_account_change():
    with Session(db.engine) as session:
        res = []

        accounts = session.query(Account).order_by(asc(Account.date)).all()
        for account in accounts:
            res.append((account.date, round(float(account.currency), 2)))
        df = pd.DataFrame(res, columns=["Date", "Currency"])
        return df


def calculate_ticker_daily_change():
    with Session(db.engine) as session:
        res = []

        stocck_asset = session.query(StockAsset).order_by(asc(StockAsset.date)).first()
        for each_date in pd.date_range(
            start=stocck_asset.date + timedelta(1), end=date.today() - timedelta(1)
        ):
            res += [
                (each_date, round(float(earn), 2), ticker)
                for earn, ticker in calculate_each_daily_change(each_date)
            ]
        df = pd.DataFrame(res, columns=["Date", "Earn", "Ticker"])
        return df


def calculate_each_daily_ticker_price(each_date: date):
    with Session(db.engine) as session:
        stock_assets = (
            session.query(StockAsset).filter(StockAsset.date == each_date).all()
        )
        res = Decimal(0)

        for stock in stock_assets:
            current_date = get_ticker_close_price(each_date, stock.ticker)

            today_exchange_rate = Decimal(1)
            if current_date.currency_type != CurrencyType.USD:
                today_exchange_rate = (
                    session.query(ExchangedRate)
                    .filter(ExchangedRate.currency_type == current_date.currency_type)
                    .filter(ExchangedRate.date == each_date + timedelta(1))
                    .first()
                    .rate
                )

            res += (current_date.currency / today_exchange_rate) * stock.shares

        return res


def calculate_each_daily_change(each_date: date):
    with Session(db.engine) as session:
        stock_assets = (
            session.query(StockAsset).filter(StockAsset.date == each_date).all()
        )
        res = []

        for stock in stock_assets:
            yesterday = get_ticker_close_price(each_date - timedelta(1), stock.ticker)
            current_date = get_ticker_close_price(each_date, stock.ticker)

            yesterday_exchange_rate = Decimal(1)
            today_exchange_rate = Decimal(1)
            if current_date.currency_type != CurrencyType.USD:
                yesterday_exchange_rate = (
                    session.query(ExchangedRate)
                    .filter(ExchangedRate.currency_type == current_date.currency_type)
                    .filter(ExchangedRate.date == each_date)
                    .first()
                    .rate
                )
                today_exchange_rate = (
                    session.query(ExchangedRate)
                    .filter(ExchangedRate.currency_type == current_date.currency_type)
                    .filter(ExchangedRate.date == each_date + timedelta(1))
                    .first()
                    .rate
                )

            res.append(
                (
                    (
                        current_date.currency / today_exchange_rate
                        - yesterday.currency / yesterday_exchange_rate
                    )
                    * stock.shares,
                    stock.ticker,
                )
            )

        return res
