import datetime
import enum
from decimal import Decimal

from sqlalchemy import Date, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from db.common import Base, DecimalAsString


class Config(Base):
    __tablename__ = "config"

    key: Mapped[str] = mapped_column(String, nullable=True)
    value: Mapped[str] = mapped_column(String, nullable=True)


class CurrencyType(enum.Enum):
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
    currency_type: Mapped[CurrencyType] = mapped_column(
        Enum(CurrencyType), nullable=False, comment="货币单位"
    )


class AssetType(enum.Enum):
    TICKER = "ticker"
    CURRENCY = "currency"


class Asset(Base):
    __tablename__ = "asset"

    date: Mapped[datetime.date] = mapped_column(
        Date, nullable=False, comment="资产记录时间"
    )
    type: Mapped[AssetType] = mapped_column(Enum(AssetType), nullable=False)
    comment: Mapped[str] = mapped_column(String, nullable=True, comment="持有资产评论")

    __mapper_args__ = {
        "polymorphic_on": type,
    }


class StockAsset(Asset):
    __mapper_args__ = {
        "polymorphic_identity": AssetType.TICKER,
    }

    ticker: Mapped[str] = mapped_column(String(20), nullable=True, comment="股票代码")
    shares: Mapped[Decimal] = mapped_column(
        DecimalAsString, nullable=True, comment="股票份额"
    )
    price: Mapped[Decimal] = mapped_column(
        DecimalAsString, nullable=True, comment="平均价格"
    )


class CurrencyAsset(Asset):
    __mapper_args__ = {
        "polymorphic_identity": AssetType.CURRENCY,
    }

    currency: Mapped[Decimal] = mapped_column(
        DecimalAsString, nullable=True, comment="货币金额"
    )
    currency_type: Mapped[CurrencyType] = mapped_column(
        Enum(CurrencyType), nullable=True, comment="货币单位"
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
    comment: Mapped[str] = mapped_column(String, nullable=True, comment="购买备注")

    __mapper_args__ = {
        "polymorphic_on": trade_type,
    }


class StockTransaction(Transaction):
    __mapper_args__ = {
        "polymorphic_identity": AssetType.TICKER,
    }

    ticker: Mapped[str] = mapped_column(String(20), nullable=True, comment="股票代码")
    shares: Mapped[Decimal] = mapped_column(
        DecimalAsString, nullable=True, comment="股票份额"
    )
    price: Mapped[Decimal] = mapped_column(
        DecimalAsString, nullable=True, comment="交易价格"
    )


class CurrencyTransaction(Transaction):
    __mapper_args__ = {
        "polymorphic_identity": AssetType.CURRENCY,
    }

    currency: Mapped[Decimal] = mapped_column(
        DecimalAsString, nullable=True, comment="货币金额"
    )
    currency_type: Mapped[CurrencyType] = mapped_column(
        Enum(CurrencyType), nullable=True, comment="货币单位"
    )


class ExchangedRate(Base):
    __tablename__ = "exchanged_rate"

    currency_type: Mapped[CurrencyType] = mapped_column(
        Enum(CurrencyType), nullable=False, comment="美元兑换的货币单位"
    )
    rate: Mapped[Decimal] = mapped_column(
        DecimalAsString, nullable=False, comment="货币汇率"
    )
    date: Mapped[datetime.date] = mapped_column(
        Date, nullable=False, comment="对应日期"
    )


class TickerInfo(Base):
    __tablename__ = "ticker_info"

    date: Mapped[datetime.date] = mapped_column(
        Date, nullable=False, comment="对应日期"
    )
    ticker: Mapped[str] = mapped_column(String(20), nullable=True, comment="股票代码")
    currency: Mapped[Decimal] = mapped_column(
        DecimalAsString, nullable=True, comment="货币金额"
    )
    currency_type: Mapped[CurrencyType] = mapped_column(
        Enum(CurrencyType), nullable=False, comment="美元兑换的货币单位"
    )
