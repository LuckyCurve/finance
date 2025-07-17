# 执行对应的同步任务，将数据从外部数据源同步到数据库当中来


import datetime
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, List

import pandas as pd
from sqlalchemy import asc, func, select
from sqlalchemy.orm import Session

import db
from adaptor.outbound import currency
from adaptor.outbound.ticker import (
    get_all_hk_symbols,
    get_all_us_symbols,
    get_hk_ticker_history,
    get_us_ticker_history,
)
from db import engine
from db.entity import (
    Account,
    Asset,
    Config,
    CurrencyAsset,
    CurrencyTransaction,
    CurrencyType,
    ExchangedRate,
    StockAsset,
    StockTransaction,
    TickerInfo,
    TickerSymbol,
    TickerType,
    Transaction,
    TransactionType,
)
from service.ticker import get_ticker_close_price
from utils.timing import timing_decorator

LAST_SYNC_DATE = "last_sync_date"

DATE_FORMAT = "%Y-%m-%d"


def sync():
    with Session(db.engine) as session:
        sync_config = session.query(Config).filter(Config.key == LAST_SYNC_DATE).first()
        if sync_config is not None:
            sync_date = datetime.datetime.strptime(
                sync_config.value, DATE_FORMAT
            ).date()
            if sync_date >= date.today():
                print("检测到已经同步，跳过同步信息")
                return
        else:
            sync_config = Config(key=LAST_SYNC_DATE)

        sync_exchange_rate()
        sync_ticker_info()
        sync_asset()
        sync_account()

        sync_config.value = date.today().strftime(DATE_FORMAT)
        if sync_config.id is None:
            session.add(sync_config)
        session.commit()
        print("所有数据均同步成功!")


@timing_decorator
def sync_account():
    with Session(db.engine) as session:
        session.query(Account).delete()
        assets = session.query(Asset).order_by(asc(Asset.date)).first()

        # 预加载所有需要的汇率数据
        all_exchange_rates = (
            session.query(ExchangedRate)
            .filter(ExchangedRate.date >= assets.date)
            .filter(ExchangedRate.date < date.today())
            .all()
        )
        exchange_rates_by_date_currency = {}
        for rate_entry in all_exchange_rates:
            if rate_entry.date not in exchange_rates_by_date_currency:
                exchange_rates_by_date_currency[rate_entry.date] = {}
            exchange_rates_by_date_currency[rate_entry.date][
                rate_entry.currency_type
            ] = rate_entry.rate

        for each_date in pd.date_range(
            start=assets.date, end=date.today() - timedelta(1)
        ):
            current_day_exchange_rates = exchange_rates_by_date_currency.get(
                each_date.date(), {}
            )
            session.add(
                Account(
                    date=each_date,
                    currency=_calculate_stock_each_daily_account(
                        each_date, session, current_day_exchange_rates
                    )
                    + _calculate_currency_each_daily_account(
                        each_date, session, current_day_exchange_rates
                    ),
                    currency_type=CurrencyType.USD,
                )
            )
        session.commit()


def _calculate_currency_each_daily_account(
    each_date: date, session: Session, exchange_rates_map: Dict[CurrencyType, Decimal]
):
    currency_assets = (
        session.query(CurrencyAsset).filter(CurrencyAsset.date == each_date).all()
    )
    res = Decimal(0)

    for currency_asset in currency_assets:
        exchange_rate = Decimal(1)
        if not currency_asset.currency_type == CurrencyType.USD:
            exchange_rate = exchange_rates_map.get(currency_asset.currency_type, Decimal(1))
        res += currency_asset.currency / exchange_rate

    return res


def _calculate_stock_each_daily_account(
    each_date: date, session: Session, exchange_rates_map: Dict[CurrencyType, Decimal]
):
    stock_assets = session.query(StockAsset).filter(StockAsset.date == each_date).all()
    res = Decimal(0)

    for stock in stock_assets:
        current_date = get_ticker_close_price(each_date, stock.ticker)

        exchange_rate = Decimal(1)
        if current_date.currency_type != CurrencyType.USD:
            exchange_rate = exchange_rates_map.get(current_date.currency_type, Decimal(1))
        res += current_date.currency * stock.shares / exchange_rate

    return res


@timing_decorator
def sync_asset():
    with Session(engine) as session:
        session.query(Asset).delete()

        count = session.query(Transaction).count()
        if count == 0:
            raise Exception("交易记录为空，无法生成资产数据")

        _sync_stock_asset(session)
        _sync_currency_asset(session)
        session.commit()


def _sync_currency_asset(session):
    currency_transactions = (
        session.query(CurrencyTransaction).order_by(asc(CurrencyTransaction.date)).all()
    )
    if not currency_transactions:
        return

    df = pd.DataFrame(
        [
            {
                "date": t.date,
                "currency_type": t.currency_type,
                "amount": t.currency if t.type == TransactionType.BUY else -t.currency,
            }
            for t in currency_transactions
        ]
    )

    # 确保日期是 datetime 类型以便进行日期范围操作
    df["date"] = pd.to_datetime(df["date"])

    # 创建一个完整的日期范围
    full_date_range = pd.date_range(
        start=df["date"].min(), end=date.today()
    )

    # 对每个货币类型进行处理
    all_assets = []
    for currency_type in df["currency_type"].unique():
        currency_df = df[df["currency_type"] == currency_type].copy()
        
        # 按日期分组并求和，得到每日净变动
        daily_changes = currency_df.groupby("date")["amount"].sum().reindex(full_date_range, fill_value=0)
        
        # 计算累积和得到每日资产
        daily_assets = daily_changes.cumsum()

        # 转换为 CurrencyAsset 对象
        for d, amount in daily_assets.items():
            all_assets.append(
                CurrencyAsset(
                    date=d.date(), currency=Decimal(str(amount)), currency_type=currency_type
                )
            )
    session.add_all(all_assets)


def _sync_stock_asset(session):
    stock_transactions = (
        session.query(StockTransaction).order_by(asc(StockTransaction.date)).all()
    )
    if not stock_transactions:
        return

    df = pd.DataFrame(
        [
            {
                "date": t.date,
                "ticker": t.ticker,
                "shares": t.shares if t.type == TransactionType.BUY else -t.shares,
                "price": t.price,
                "transaction_type": t.type,
            }
            for t in stock_transactions
        ]
    )

    df["date"] = pd.to_datetime(df["date"])

    # 对同一天同一股票的多笔交易进行聚合
    # 对于 shares，直接求和
    # 对于 price，计算加权平均
    aggregated_df = (
        df.groupby(["date", "ticker"], as_index=False) # Use as_index=False to keep grouping columns as regular columns
        .apply(
            lambda x: pd.Series(
                {
                    "shares_change": x["shares"].sum(),
                    "weighted_price": (x["shares"] * x["price"]).sum()
                    / x["shares"].sum()
                    if x["shares"].sum() != 0
                    else Decimal(0),
                    "transaction_type": x["transaction_type"].iloc[0], # Take the first transaction type, assuming consistency
                }
            ),
            include_groups=False # Explicitly exclude grouping columns from the result of apply
        )
    )
    # If as_index=False is used, reset_index() might not be needed, but it's safer to keep it if the structure changes
    # aggregated_df = aggregated_df.reset_index()

    full_date_range = pd.date_range(start=df["date"].min(), end=date.today())

    all_assets = []
    for ticker_symbol in aggregated_df["ticker"].unique():
        ticker_df = aggregated_df[aggregated_df["ticker"] == ticker_symbol].copy()

        # 确保所有日期都在 full_date_range 中，并填充缺失日期
        ticker_df = ticker_df.set_index("date").reindex(full_date_range).reset_index()
        ticker_df = ticker_df.rename(columns={"index": "date"})

        # 初始化每日持股数量和成本
        current_shares = Decimal(0)
        current_cost = Decimal(0)

        for _, row in ticker_df.iterrows():
            if pd.isna(row["shares_change"]):  # 如果是缺失日期，则沿用前一天的资产状态
                pass
            else:
                shares_change = Decimal(str(row["shares_change"]))
                price = Decimal(str(row["weighted_price"]))
                transaction_type = row["transaction_type"]

                if transaction_type == TransactionType.BUY:
                    new_total_shares = current_shares + shares_change
                    if new_total_shares != 0:
                        current_cost = (current_cost * current_shares + price * shares_change) / new_total_shares
                    else:
                        current_cost = Decimal(0)
                    current_shares = new_total_shares
                elif transaction_type == TransactionType.SELL:
                    if current_shares < shares_change:
                        raise Exception(
                            f"transaction 数据出现异常，当前持有资产不足以出售，id: {row.get('id', 'N/A')}"
                        )
                    current_shares -= shares_change
                    # 卖出不改变平均成本，除非全部卖出
                    if current_shares == 0:
                        current_cost = Decimal(0)
                else:
                    # 对于其他未处理的交易类型，可以抛出异常或记录日志
                    pass

            all_assets.append(
                StockAsset(
                    ticker=ticker_symbol,
                    shares=Decimal(str(current_shares)),
                    date=row["date"].date(),
                    price=Decimal(str(current_cost)),
                )
            )
    session.add_all(all_assets)


@timing_decorator
def sync_exchange_rate() -> None:
    with Session(engine) as session:
        session.query(ExchangedRate).delete()

        cloest_date = (
            session.query(Transaction).order_by(asc(Transaction.date)).first().date
        )

        exchanged_rates = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = executor.map(
                currency.get_exchange_rate,
                list(pd.date_range(start=cloest_date, end=date.today() - timedelta(1))),
            )

            for result in results:
                exchanged_rates += [
                    ExchangedRate(
                        currency_type=currency_type, rate=rate, date=result[0]
                    )
                    for currency_type, rate in result[1].items()
                ]

        session.add_all(exchanged_rates)

        session.commit()


@timing_decorator
def sync_ticker_info():
    sync_hk_ticker_symbol()
    sync_us_ticker_symbol()

    with Session(db.engine) as session:
        sql = select(StockTransaction.ticker, func.min(StockTransaction.date)).group_by(
            StockTransaction.ticker
        )

        session.query(TickerInfo).delete()
        all_ticker_infos = []

        ticker_data_to_fetch = []
        for ticker_name, buy_date in session.execute(sql).all():
            symbol = search_ticker_symbol(ticker_name)
            ticker_data_to_fetch.append((ticker_name, buy_date, symbol))

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for ticker_name, buy_date, symbol in ticker_data_to_fetch:
                if symbol.ticker_type == TickerType.USD:
                    futures.append(
                        executor.submit(
                            get_us_ticker_history,
                            symbol.symbol,
                            start_date=buy_date,
                            end_date=date.today() - timedelta(1),
                        )
                    )
                elif symbol.ticker_type == TickerType.HKD:
                    futures.append(
                        executor.submit(
                            get_hk_ticker_history,
                            symbol.symbol,
                            start_date=buy_date,
                            end_date=date.today() - timedelta(1),
                        )
                    )

            for i, future in enumerate(futures):
                ticker_name, _, symbol = ticker_data_to_fetch[i]
                ticker_infos_for_symbol = future.result()
                currency_type = (
                    CurrencyType.USD
                    if symbol.ticker_type == TickerType.USD
                    else CurrencyType.HKD
                )

                all_ticker_infos.extend(
                    [
                        TickerInfo(
                            date=date,
                            ticker=ticker_name,
                            currency=Decimal(price),
                            currency_type=currency_type,
                        )
                        for (date, price) in ticker_infos_for_symbol
                    ]
                )
        session.add_all(all_ticker_infos)
        session.commit()


def search_ticker_symbol(symbol: str) -> TickerSymbol:
    with Session(db.engine) as session:
        return (
            session.query(TickerSymbol)
            .filter(TickerSymbol.symbol.like(f"%{symbol}"))
            .first()
        )


def sync_us_ticker_symbol():
    with Session(db.engine) as session:
        count = (
            session.query(TickerSymbol)
            .filter(TickerSymbol.ticker_type == TickerType.USD)
            .count()
        )

        if count > 0:
            return

        session.add_all(
            [
                TickerSymbol(symbol=symbol, name=name, ticker_type=TickerType.USD)
                for (name, symbol) in get_all_us_symbols()
            ]
        )

        session.commit()


def sync_hk_ticker_symbol():
    with Session(db.engine) as session:
        count = (
            session.query(TickerSymbol)
            .filter(TickerSymbol.ticker_type == TickerType.HKD)
            .count()
        )

        if count > 0:
            return

        session.add_all(
            [
                TickerSymbol(symbol=symbol, name=name, ticker_type=TickerType.HKD)
                for (name, symbol) in get_all_hk_symbols()
            ]
        )

        session.commit()
