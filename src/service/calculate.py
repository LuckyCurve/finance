from datetime import date, timedelta
from decimal import Decimal

import pandas as pd
from sqlalchemy import asc
from sqlalchemy.orm import Session

import db
from db.entity import CurrencyType, ExchangedRate, StockAsset
from service.ticker import get_ticker_close_price


def calculate_daily_change():
    with Session(db.engine) as session:
        stocck_asset = session.query(StockAsset).order_by(asc(StockAsset.date)).first()
        for each_date in pd.date_range(
            start=stocck_asset.date + timedelta(1), end=date.today() - timedelta(1)
        ):
            print(
                f"date: {each_date} - {calculate_each_daily_change(each_date, session)}"
            )


def calculate_each_daily_change(each_date: date, session: Session):
    stock_assets = session.query(StockAsset).filter(StockAsset.date == each_date).all()
    res = Decimal(0)

    for stock in stock_assets:
        yesterday = get_ticker_close_price(each_date - timedelta(1), stock.ticker)
        current_date = get_ticker_close_price(each_date, stock.ticker)

        exchange_rate = Decimal(1)
        if yesterday.currency_type != CurrencyType.USD:
            exchange_rate = (
                session.query(ExchangedRate)
                .filter(ExchangedRate.currency_type == yesterday.currency_type)
                .filter(ExchangedRate.date == each_date + timedelta(1))
                .first()
                .rate
            )
        res += (
            (current_date.currency - yesterday.currency) * stock.shares / exchange_rate
        )

    return res
