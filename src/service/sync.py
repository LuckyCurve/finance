# 执行对应的同步任务，将数据从外部数据源同步到数据库当中来


from datetime import date, timedelta

from sqlalchemy import desc
from sqlalchemy.orm import Session

from db import engine
from db.entity import ExchangedRate
from outbound import currency


def sync_exchange_rate() -> None:
    with Session(engine) as session:
        count = session.query(ExchangedRate).count()
        if count == 0:
            session.add_all(
                [
                    ExchangedRate(
                        currency_type=currency_type, rate=rate, date=date.today()
                    )
                    for currency_type, rate in currency.get_currency(
                        date.today()
                    ).items()
                ]
            )
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
