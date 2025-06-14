from datetime import date, timedelta
from decimal import Decimal

import pandas as pd
from sqlalchemy import asc
from sqlalchemy.orm import Session

import db
from db.entity import CurrencyType, ExchangedRate, StockAsset
from service.ticker import get_ticker_close_price


def calculate_ticker_daily_change():
    with Session(db.engine) as session:
        res = []

        stocck_asset = session.query(StockAsset).order_by(asc(StockAsset.date)).first()
        for each_date in pd.date_range(
            start=stocck_asset.date + timedelta(1), end=date.today() - timedelta(1)
        ):
            res.append(
                (
                    each_date,
                    round(float(calculate_each_daily_change(each_date, session)), 2),
                )
            )
        return res


def calculate_each_daily_change(each_date: date, session: Session):
    stock_assets = session.query(StockAsset).filter(StockAsset.date == each_date).all()
    res = Decimal(0)

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

        #  这里需要注意的是：每日股票涨跌幅不仅受到股价涨跌的影响，也受到汇率涨跌的影响
        res += (
            current_date.currency / today_exchange_rate
            - yesterday.currency / yesterday_exchange_rate
        ) * stock.shares

    return res
