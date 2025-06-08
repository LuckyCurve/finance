from datetime import date
from decimal import Decimal
from enum import Enum

from sqlalchemy import Date, String
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column

from db.common import Base, DecimalAsString


class TradeOperate(Enum):
    BUY = "buy"
    SELL = "sell"


class Transactions(Base):
    """记录交易信息"""

    __tablename__ = "transactions"

    symbol: Mapped[str] = mapped_column(String(256), nullable=False, comment="股票代码")
    share: Mapped[Decimal] = mapped_column(
        DecimalAsString, nullable=False, comment="股票份额"
    )
    price: Mapped[Decimal] = mapped_column(
        DecimalAsString, nullable=False, comment="当前交易股票价格"
    )
    trade_operate: Mapped[TradeOperate] = mapped_column(
        SqlEnum(TradeOperate), nullable=False, comment="交易类型"
    )


class Account(Base):
    """记录当前账户信息"""

    __tablename__ = "account"

    symbol: Mapped[str] = mapped_column(String(256), nullable=False, comment="股票代码")
    total_share: Mapped[Decimal] = mapped_column(
        DecimalAsString, nullable=False, comment="当前股票对应份额"
    )
    average_price: Mapped[Decimal] = mapped_column(
        DecimalAsString, nullable=False, comment="当前股票入手平均价格"
    )


class AccountChange(Base):
    """计算每日账户余额变化"""

    __tablename__ = "account_change"

    store_change: Mapped[Decimal] = mapped_column(
        DecimalAsString, nullable=False, comment="股票部分的波动率，不包含继续入金金额"
    )
    current_date: Mapped[date] = mapped_column(
        Date(), nullable=False, comment="账户当前变化计算时间"
    )
