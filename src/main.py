from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from db import engine
from db.common import Base
from db.entity import Account, CurrencyUnit

if __name__ == "__main__":
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        a = Account(
            date=date.today(), currency=Decimal("10"), currency_unit=CurrencyUnit.CNY
        )
        session.add(a)
        session.commit()
