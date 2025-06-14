import datetime

from sqlalchemy import desc
from sqlalchemy.orm import Session

import db
from db.entity import TickerInfo


def get_ticker_close_price(date: datetime.date, symbol: str) -> TickerInfo:
    with Session(db.engine) as session:
        current_date = (
            session.query(TickerInfo)
            .filter(TickerInfo.ticker == symbol)
            .filter(TickerInfo.date <= date)
            .order_by(desc(TickerInfo.date))
            .first()
        )
        return current_date
