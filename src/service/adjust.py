from decimal import Decimal

from sqlalchemy import desc
from sqlalchemy.orm import Session

import db
from db.entity import CurrencyAsset, CurrencyType
from service.transaction import buy_currency, sell_currency


def adjust_currency(currency: float | str, currency_type: CurrencyType):
    """进行现金金额调整,完成平账操作"""
    with Session(db.engine) as session:
        currency_asset = (
            session.query(CurrencyAsset)
            .filter(CurrencyAsset.currency_type == currency_type)
            .order_by(desc(CurrencyAsset.date))
            .limit(1)
            .first()
        )

        COMMENT = "平账操作"
        if currency_asset.currency > currency:
            sell_currency(
                currency_asset.currency - Decimal(currency), currency_type, COMMENT
            )
        elif currency_asset.currency < currency:
            buy_currency(
                Decimal(currency) - currency_asset.currency, currency_type, COMMENT
            )

    print("平账完成")
