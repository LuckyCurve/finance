import logging
from decimal import Decimal

from sqlalchemy import desc
from sqlalchemy.orm import Session

import db
from db.entity import CurrencyAsset, CurrencyType
from service.transaction import buy_currency, sell_currency


def adjust_currency(currency: float | str, currency_type: CurrencyType) -> None:
    """进行现金金额调整,完成平账操作"""
    with Session(db.engine) as session:
        currency_asset = (
            session.query(CurrencyAsset)
            .filter(CurrencyAsset.currency_type == currency_type)
            .order_by(desc(CurrencyAsset.date))
            .limit(1)
            .first()
        )

        if currency_asset is None:
            currency_asset = CurrencyAsset(
                currency_type=currency_type, currency=Decimal(0)
            )

        COMMENT = "平账操作"

        if abs(currency_asset.currency - Decimal(currency)) < 1:
            logging.info("无需平账")
            return

        if currency_asset.currency > currency:
            sell_currency(
                currency_asset.currency - Decimal(currency), currency_type, COMMENT
            )
        elif currency_asset.currency < currency:
            buy_currency(
                Decimal(currency) - currency_asset.currency, currency_type, COMMENT
            )

    logging.info("平账完成")
