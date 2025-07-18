from datetime import datetime
from decimal import Decimal

from sqlalchemy import TEXT, DateTime, TypeDecorator, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class DecimalAsString(TypeDecorator):
    impl = TEXT()  # 底层数据库类型

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if not isinstance(value, Decimal):
            value = Decimal(value)
        # 转成字符串存储
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        # 读取时转回Decimal
        return Decimal(value)


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(
        primary_key=True, nullable=False, autoincrement=True, comment="主键 id"
    )
    create_time: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="创建时间，由数据库插入时间指定"
    )
    update_time: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间，默认由程序生成"
    )
