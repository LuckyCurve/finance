import datetime
import enum
from decimal import Decimal

from sqlalchemy import Boolean, Date, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from db.common import Base, DecimalAsString


class CurrencyUnit(enum.Enum):
    CNY = "CNY"
    USD = "USD"
    HKD = "HKD"


class Account(Base):
    __tablename__ = "account"

    date: Mapped[datetime.date] = mapped_column(
        Date, nullable=False, comment="当前日期对应的账户资产"
    )
    currency: Mapped[Decimal] = mapped_column(
        DecimalAsString, nullable=False, comment="货币金额"
    )
    currency_unit: Mapped[CurrencyUnit] = mapped_column(
        Enum(CurrencyUnit), nullable=False, comment="货币单位"
    )


class AssetType(enum.Enum):
    TICKER = "ticker"
    CURRENCY = "currency"


class Asset(Base):
    __tablename__ = "asset"

    date: Mapped[datetime.date] = mapped_column(
        Date, nullable=False, comment="资产记录时间"
    )
    is_current: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        comment="是否为最新资产数据，如果没有发生交易，则始终为最新的资产数据",
    )
    type: Mapped[AssetType] = mapped_column(Enum(AssetType), nullable=False)
    comment: Mapped[str] = mapped_column(String, comment="持有资产评论")

    __mapper_args__ = {
        "polymorphic_on": type,
    }


class StockAsset(Asset):
    __mapper_args__ = {
        "polymorphic_identity": AssetType.TICKER,
    }

    ticker: Mapped[str] = mapped_column(String(20), nullable=False, comment="股票代码")
    shares: Mapped[Decimal] = mapped_column(
        DecimalAsString, nullable=False, comment="股票份额"
    )


class CurrencyAsset(Asset):
    __mapper_args__ = {
        "polymorphic_identity": AssetType.CURRENCY,
    }

    currency: Mapped[Decimal] = mapped_column(
        DecimalAsString, nullable=False, comment="货币金额"
    )
    currency_unit: Mapped[CurrencyUnit] = mapped_column(
        Enum(CurrencyUnit), nullable=False, comment="货币单位"
    )


class TransactionType(enum.Enum):
    SELL = "sell"
    BUY = "buy"


class Transaction(Base):
    __tablename__ = "transaction"

    date: Mapped[datetime.date] = mapped_column(
        Date, nullable=False, comment="交易发生时间"
    )
    type: Mapped[TransactionType] = mapped_column(Enum(TransactionType), nullable=False)
    trade_type: Mapped[AssetType] = mapped_column(Enum(AssetType), nullable=False)
    comment: Mapped[str] = mapped_column(String, comment="购买备注")

    __mapper_args__ = {
        "polymorphic_on": trade_type,
    }


class StockTransaction(Transaction):
    __mapper_args__ = {
        "polymorphic_identity": AssetType.TICKER,
    }

    ticker: Mapped[str] = mapped_column(String(20), nullable=False, comment="股票代码")
    shares: Mapped[Decimal] = mapped_column(
        DecimalAsString, nullable=False, comment="股票份额"
    )


class CurrencyTransaction(Transaction):
    __mapper_args__ = {
        "polymorphic_identity": AssetType.CURRENCY,
    }

    currency: Mapped[Decimal] = mapped_column(
        DecimalAsString, nullable=False, comment="货币金额"
    )
    currency_unit: Mapped[CurrencyUnit] = mapped_column(
        Enum(CurrencyUnit), nullable=False, comment="货币单位"
    )
