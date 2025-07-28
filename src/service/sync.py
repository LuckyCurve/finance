# 执行对应的同步任务，将数据从外部数据源同步到数据库当中来


import datetime
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from decimal import Decimal

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
from utils.timing import timing_decorator

LAST_SYNC_DATE = "last_sync_date"

DATE_FORMAT = "%Y-%m-%d"


def sync() -> None:
    """
    执行所有数据同步任务的主函数。

    同步顺序:
    1. 汇率 (sync_exchange_rate): 必须先同步，因为后续资产计算需要用到。
    2. 股票代码 (sync_ticker_symbol): 同步股票的基本信息。
    3. 股票历史价格 (sync_ticker_info): 依赖股票代码，为后续计算提供每日价格。
    4. 每日资产快照 (sync_asset): 依赖交易记录，计算每日持仓。
    5. 每日账户总价值 (sync_account): 依赖资产快照、股票价格和汇率，计算最终的每日总价值。
    """
    with Session(db.engine) as session:
        # 检查上次同步日期，如果今天已经同步过，则跳过
        if _is_already_synced(session):
            logging.info("检测到今日已同步，跳过任务。")
            return

        logging.info("开始执行数据同步任务...")
        # 按照正确的依赖顺序执行同步
        sync_exchange_rate()
        sync_ticker_info()  # sync_ticker_symbol 包含在其中
        sync_asset()
        sync_account()

        # 更新同步状态
        _update_sync_status(session)
        logging.info("所有数据均同步成功!")


def _is_already_synced(session: Session) -> bool:
    """检查今天是否已经执行过同步。"""
    sync_config = session.query(Config).filter(Config.key == LAST_SYNC_DATE).first()
    if sync_config:
        try:
            last_sync_date = datetime.datetime.strptime(
                sync_config.value, DATE_FORMAT
            ).date()
            return last_sync_date >= date.today()
        except (ValueError, TypeError):
            # 如果日期格式错误或值为 None，则认为未同步
            return False
    return False


def _update_sync_status(session: Session) -> None:
    """更新同步状态到今天的日期。"""
    sync_config = session.query(Config).filter(Config.key == LAST_SYNC_DATE).first()
    if sync_config is None:
        # 如果配置项不存在，则创建一个新的
        sync_config = Config(key=LAST_SYNC_DATE)
        session.add(sync_config)

    sync_config.value = date.today().strftime(DATE_FORMAT)
    session.commit()


@timing_decorator
def sync_account() -> None:
    """
    基于每日资产快照（Asset）和股票价格（TickerInfo），计算每日的总账户价值（Account）。
    所有资产都会被换算成美元（USD）进行汇总。
    """
    with Session(db.engine) as session:
        # 清空旧的账户数据
        session.query(Account).delete()

        # 获取首次资产记录的日期，作为计算的起始点
        first_asset = session.query(Asset).order_by(asc(Asset.date)).first()
        if not first_asset:
            logging.warning("警告: 资产数据为空，无法计算账户价值。")
            return

        start_date = first_asset.date
        end_date = date.today() - timedelta(1)

        # 1. 预加载所有需要的数据到内存中，避免循环查询
        all_assets = session.query(Asset).filter(Asset.date >= start_date).all()
        all_ticker_infos = (
            session.query(TickerInfo).filter(TickerInfo.date >= start_date).all()
        )
        all_exchange_rates = (
            session.query(ExchangedRate).filter(ExchangedRate.date >= start_date).all()
        )

        # 2. 将数据转换为更易于查询的结构（字典）
        assets_by_date = _group_by_date(all_assets)
        ticker_prices_by_date_ticker = _group_ticker_prices(all_ticker_infos)
        rates_by_date_currency = _group_exchange_rates(all_exchange_rates)

        # 3. 迭代每一天，计算当天的总账户价值
        new_accounts = []
        for each_date in pd.date_range(start=start_date, end=end_date):
            d = each_date.date()
            daily_assets = assets_by_date.get(d, [])
            if not daily_assets:
                continue  # 如果当天没有资产记录，则跳过

            # 获取当天的汇率和股票价格
            daily_rates = rates_by_date_currency.get(d, {})
            daily_ticker_prices = ticker_prices_by_date_ticker.get(d, {})

            # 计算当天的总价值
            total_value_usd = _calculate_daily_total_value(
                daily_assets, daily_ticker_prices, daily_rates
            )

            new_accounts.append(
                Account(
                    date=d,
                    currency=total_value_usd,
                    currency_type=CurrencyType.USD,
                )
            )

        # 4. 批量存入数据库
        if new_accounts:
            session.add_all(new_accounts)
            session.commit()
            logging.info(f"成功同步 {len(new_accounts)} 条账户价值记录。")


def _calculate_daily_total_value(
    daily_assets: list[Asset],
    daily_ticker_prices: dict[str, TickerInfo],
    daily_rates: dict[CurrencyType, Decimal],
) -> Decimal:
    """计算给定一天所有资产的总价值（换算成美元）。"""
    total_value = Decimal(0)
    for asset in daily_assets:
        if isinstance(asset, StockAsset):
            # 计算股票资产价值
            ticker_info = daily_ticker_prices.get(asset.ticker)
            if ticker_info and asset.shares > 0:
                price = ticker_info.currency
                value = price * asset.shares
                # 换算成美元
                total_value += _convert_to_usd(
                    value, ticker_info.currency_type, daily_rates
                )
        elif isinstance(asset, CurrencyAsset):
            # 计算现金资产价值
            if asset.currency > 0:
                total_value += _convert_to_usd(
                    asset.currency, asset.currency_type, daily_rates
                )
    return total_value


def _convert_to_usd(
    value: Decimal, currency_type: CurrencyType, rates: dict[CurrencyType, Decimal]
) -> Decimal:
    """将给定金额从指定货币换算成美元。"""
    if currency_type == CurrencyType.USD:
        return value
    rate = rates.get(currency_type)
    if rate is None or rate == 0:
        logging.warning(f"警告: 找不到货币 {currency_type} 的汇率，无法换算。")
        return Decimal(0)
    return value / rate


def _group_by_date(items: list) -> dict[date, list]:
    """将列表按日期分组。"""
    grouped = {}
    for item in items:
        grouped.setdefault(item.date, []).append(item)
    return grouped


def _group_ticker_prices(
    ticker_infos: list[TickerInfo],
) -> dict[date, dict[str, TickerInfo]]:
    """将股票价格信息按日期和股票代码两级分组。"""
    grouped = {}
    for info in ticker_infos:
        if info.date not in grouped:
            grouped[info.date] = {}
        grouped[info.date][info.ticker] = info
    return grouped


def _group_exchange_rates(
    exchange_rates: list[ExchangedRate],
) -> dict[date, dict[CurrencyType, Decimal]]:
    """将汇率信息按日期和货币类型两级分组。"""
    grouped = {}
    for rate in exchange_rates:
        if rate.date not in grouped:
            grouped[rate.date] = {}
        grouped[rate.date][rate.currency_type] = rate.rate
    return grouped


@timing_decorator
def sync_asset() -> None:
    """
    根据交易记录同步每日的资产快照。
    该函数会清空现有的资产数据，然后根据所有的股票和现金交易记录，
    重新计算从第一笔交易开始到昨天为止的每一天的资产状况。
    """
    with Session(engine) as session:
        # 清空旧的资产数据
        session.query(Asset).delete()

        # 检查是否有交易记录，没有则无法继续
        if session.query(Transaction).count() == 0:
            logging.warning("警告: 交易记录为空，无法生成资产数据。")
            return

        # 分别同步股票和现金资产
        all_assets = []
        all_assets.extend(_sync_stock_asset(session))
        all_assets.extend(_sync_currency_asset(session))

        # 批量添加到数据库
        if all_assets:
            session.add_all(all_assets)
            session.commit()
            logging.info(f"成功同步 {len(all_assets)} 条资产记录。")
        else:
            logging.info("没有生成任何资产记录。")


def _sync_currency_asset(session: Session) -> list[CurrencyAsset]:
    """
    根据现金交易记录，计算每日的现金资产。
    使用 pandas 来高效处理时间序列数据。
    """
    # 1. 从数据库获取所有现金交易记录
    currency_transactions = session.query(CurrencyTransaction).all()
    if not currency_transactions:
        return []

    # 2. 将交易记录转换为 DataFrame
    df = pd.DataFrame(
        [
            {
                "date": t.date,
                "currency_type": t.currency_type,
                # 买入为正，卖出（支出）为负
                "amount": t.currency if t.type == TransactionType.BUY else -t.currency,
            }
            for t in currency_transactions
        ]
    )
    df["date"] = pd.to_datetime(df["date"])

    # 3. 创建一个从首次交易到昨天的完整日期范围
    start_date = df["date"].min()
    end_date = date.today() - timedelta(1)
    if pd.isna(start_date) or start_date.date() > end_date:
        return []
    full_date_range = pd.date_range(start=start_date, end=end_date)

    # 4. 按货币类型分别处理，并计算每日累计资产
    all_assets = []
    for currency_type, group in df.groupby("currency_type", sort=False):
        # 按日期聚合，计算每日净变动
        daily_changes = (
            group.groupby("date")["amount"].sum().reindex(full_date_range, fill_value=0)
        )
        # 计算每日累计资产
        daily_assets = daily_changes.cumsum()

        # 5. 转换为 CurrencyAsset 对象
        for d, amount in daily_assets.items():
            all_assets.append(
                CurrencyAsset(
                    date=d.date(),
                    currency=Decimal(str(amount)),
                    currency_type=currency_type,
                )
            )
    return all_assets


def _sync_stock_asset(session: Session) -> list[StockAsset]:
    """
    根据股票交易记录，计算每日的股票资产（持股数量和成本价）。
    使用 pandas 进行复杂的聚合和状态计算。
    """
    # 1. 获取所有股票交易记录
    stock_transactions = session.query(StockTransaction).all()
    if not stock_transactions:
        return []

    # 2. 将交易记录转换为 DataFrame
    df = pd.DataFrame(
        [
            {
                "date": t.date,
                "ticker": t.ticker,
                "shares": t.shares if t.type == TransactionType.BUY else -t.shares,
                "price": t.price,
            }
            for t in stock_transactions
        ]
    )
    df["date"] = pd.to_datetime(df["date"])
    df["shares"] = df["shares"].astype(str).apply(Decimal)
    df["price"] = df["price"].astype(str).apply(Decimal)

    # 3. 创建完整的日期范围
    start_date = df["date"].min()
    end_date = date.today() - timedelta(1)
    if pd.isna(start_date) or start_date.date() > end_date:
        return []
    full_date_range = pd.date_range(start=start_date, end=end_date)

    # 4. 按股票代码分别处理，计算每日持仓
    all_assets = []
    for ticker, group in df.groupby("ticker"):
        # 聚合同一天的多次交易，计算加权平均价
        daily_summary = group.groupby("date").apply(
            lambda x: pd.Series(
                {
                    "shares_change": x["shares"].sum(),
                    "weighted_price": (
                        (x["shares"] * x["price"]).sum() / x["shares"].sum()
                        if x["shares"].sum() != 0
                        else 0
                    ),
                }
            ),
            include_groups=False,
        )

        # 重新索引到完整日期范围，填充缺失值为 0
        daily_summary = daily_summary.reindex(full_date_range, fill_value=0)

        # 5. 迭代计算每日的持股数量和平均成本
        current_shares = Decimal(0)
        current_cost = Decimal(0)

        for d, row in daily_summary.iterrows():
            shares_change = Decimal(str(row["shares_change"]))
            price = Decimal(str(row["weighted_price"]))

            if shares_change != 0:
                # 计算新的总成本和总股数
                new_total_cost = (current_cost * current_shares) + (
                    price * shares_change
                )
                new_total_shares = current_shares + shares_change

                # 更新持仓和成本价
                current_shares = new_total_shares
                if current_shares != 0:
                    current_cost = new_total_cost / new_total_shares
                else:
                    current_cost = Decimal(0)  # 如果全部卖出，成本归零

            all_assets.append(
                StockAsset(
                    ticker=ticker,
                    shares=current_shares,
                    date=d.date(),
                    price=current_cost,
                )
            )
    return all_assets


@timing_decorator
def sync_exchange_rate() -> None:
    """
    同步从首次交易日期到昨天为止的每日汇率数据。
    """
    with Session(engine) as session:
        # 1. 确定需要同步汇率的日期范围
        first_transaction = (
            session.query(Transaction).order_by(asc(Transaction.date)).first()
        )
        if not first_transaction:
            logging.warning("警告: 交易记录为空，无法确定同步汇率的起始日期。")
            return

        start_date = first_transaction.date
        end_date = date.today() - timedelta(1)
        date_range = list(pd.date_range(start=start_date, end=end_date))

        if not date_range:
            return

        # 2. 使用线程池并发获取汇率数据
        logging.info(f"正在同步从 {start_date} 到 {end_date} 的汇率数据...")
        with ThreadPoolExecutor(max_workers=10) as executor:
            # map 会保持原始的提交顺序
            results = executor.map(currency.get_exchange_rate, date_range)

        # 3. 处理获取到的数据并准备入库
        exchanged_rates = []
        for result in results:
            if result and result[1]:  # 确保结果不为空
                rate_date, rates_map = result
                for currency_type, rate in rates_map.items():
                    exchanged_rates.append(
                        ExchangedRate(
                            currency_type=currency_type, rate=rate, date=rate_date
                        )
                    )

        # 4. 批量存入数据库
        if exchanged_rates:
            session.query(ExchangedRate).delete()  # 先清空旧数据
            session.add_all(exchanged_rates)
            session.commit()
            logging.info(f"成功同步 {len(exchanged_rates)} 条汇率记录。")
        else:
            logging.info("未能获取到任何汇率数据。")


@timing_decorator
def sync_ticker_info() -> None:
    """
    同步所有持仓股票的历史价格信息。
    1. 从数据库中获取需要同步的股票列表及其首次购买日期。
    2. 并发地从外部 API 获取这些股票的历史价格。
    3. 对获取到的价格数据进行处理，填充缺失的日期（如周末、节假日）。
    4. 将处理后的数据存入数据库。
    """
    # 同步最新的港股和美股的 symbol 列表
    sync_hk_ticker_symbol()
    sync_us_ticker_symbol()

    with Session(db.engine) as session:
        # 1. 获取需要同步的股票列表
        ticker_data_to_fetch = _get_ticker_data_to_fetch(session)
        if not ticker_data_to_fetch:
            logging.info("没有需要同步的股票信息。")
            return

        # 2. 并发获取所有股票的历史价格
        all_ticker_infos = _fetch_and_process_ticker_histories(ticker_data_to_fetch)

        # 3. 批量存入数据库
        if all_ticker_infos:
            session.query(TickerInfo).delete()
            session.add_all(all_ticker_infos)
            session.commit()
            logging.info(f"成功同步 {len(all_ticker_infos)} 条股票价格信息。")
        else:
            logging.info("没有获取到任何股票价格信息。")


def _get_ticker_data_to_fetch(session: Session) -> list[tuple[str, date, TickerSymbol]]:
    """从数据库中查询需要获取历史价格的股票列表。"""
    # 查询每只股票的首次交易日期
    sql = select(StockTransaction.ticker, func.min(StockTransaction.date)).group_by(
        StockTransaction.ticker
    )
    results = []
    for ticker_name, buy_date in session.execute(sql).all():
        symbol = search_ticker_symbol(ticker_name)
        if symbol:
            results.append((ticker_name, buy_date, symbol))
        else:
            logging.warning(
                f"警告: 在 TickerSymbol 表中找不到 {ticker_name} 的信息，跳过同步。"
            )
    return results


def _fetch_and_process_ticker_histories(
    ticker_data_to_fetch: list[tuple[str, date, TickerSymbol]],
) -> list[TickerInfo]:
    """并发获取并处理所有股票的历史价格。"""
    all_ticker_infos = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        # 为每个 ticker 创建一个 future
        future_to_ticker = {
            executor.submit(
                _fetch_single_ticker_history, ticker_name, buy_date, symbol
            ): (ticker_name, buy_date, symbol)
            for ticker_name, buy_date, symbol in ticker_data_to_fetch
        }

        for future in future_to_ticker:
            processed_infos = future.result()
            if processed_infos:
                all_ticker_infos.extend(processed_infos)

    return all_ticker_infos


def _fetch_single_ticker_history(
    ticker_name: str, buy_date: date, symbol: TickerSymbol
) -> list[TickerInfo] | None:
    """获取单只股票的历史数据并进行处理。"""
    history_fetcher = (
        get_us_ticker_history
        if symbol.ticker_type == TickerType.USD
        else get_hk_ticker_history
    )
    currency_type = (
        CurrencyType.USD if symbol.ticker_type == TickerType.USD else CurrencyType.HKD
    )

    try:
        # 从 API 获取原始历史数据
        raw_history = history_fetcher(
            symbol.symbol,
            start_date=buy_date,
            end_date=date.today() - timedelta(1),
        )
        if not raw_history:
            logging.warning(f"警告: 未找到 {ticker_name} 的历史数据。")
            return None

        # 填充缺失的价格数据
        return _fill_missing_ticker_prices(
            raw_history, buy_date, ticker_name, currency_type
        )
    except Exception as e:
        logging.error(f"错误: 获取 {ticker_name} 历史数据时出错: {e}")
        return None


def _fill_missing_ticker_prices(
    raw_history: list[tuple[date, float]],
    start_date: date,
    ticker_name: str,
    currency_type: CurrencyType,
) -> list[TickerInfo]:
    """使用 pandas 填充股票价格中的缺失日期（周末、节假日）。"""
    # 创建 DataFrame
    df = pd.DataFrame(raw_history, columns=["date", "price"])
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date")

    # 创建从首次购买日到昨天的完整日期范围
    full_range = pd.date_range(
        start=start_date, end=date.today() - timedelta(1), freq="D"
    )

    # 重新索引以包含所有日期，并向前填充缺失的价格
    df = df.reindex(full_range)
    df["price"] = df["price"].ffill()

    # 将填充后的数据转换为 TickerInfo 对象列表
    filled_infos = []
    for idx, row in df.iterrows():
        if pd.notna(row["price"]):
            filled_infos.append(
                TickerInfo(
                    date=idx.date(),
                    ticker=ticker_name,
                    currency=Decimal(str(row["price"])),
                    currency_type=currency_type,
                )
            )
    return filled_infos


def search_ticker_symbol(symbol: str) -> TickerSymbol | None:
    """根据股票代码模糊查询对应的 TickerSymbol 对象。"""
    with Session(db.engine) as session:
        return (
            session.query(TickerSymbol)
            .filter(TickerSymbol.symbol.like(f"%{symbol}"))
            .first()
        )


def sync_us_ticker_symbol() -> None:
    """同步所有美国的股票代码和名称。"""
    _sync_ticker_symbols(TickerType.USD, get_all_us_symbols)


def sync_hk_ticker_symbol() -> None:
    """同步所有香港的股票代码和名称。"""
    _sync_ticker_symbols(TickerType.HKD, get_all_hk_symbols)


def _sync_ticker_symbols(ticker_type: TickerType, fetch_symbols_func: callable) -> None:
    """
    同步指定类型的股票代码和名称的通用函数。

    Args:
        ticker_type: 要同步的股票类型 (USD or HKD)。
        fetch_symbols_func: 用于获取股票代码列表的函数。
    """
    with Session(db.engine) as session:
        # 检查数据库中是否已存在该类型的股票代码
        count = (
            session.query(TickerSymbol)
            .filter(TickerSymbol.ticker_type == ticker_type)
            .count()
        )
        if count > 0:
            logging.info(f"已找到 {ticker_type.value} 类型的股票代码，跳过同步。")
            return

        # 如果不存在，则从外部 API 获取并存入数据库
        logging.info(f"正在从外部 API 同步 {ticker_type.value} 类型的股票代码...")
        symbols_to_add = [
            TickerSymbol(symbol=symbol, name=name, ticker_type=ticker_type)
            for (name, symbol) in fetch_symbols_func()
        ]

        if symbols_to_add:
            session.add_all(symbols_to_add)
            session.commit()
            logging.info(
                f"成功同步 {len(symbols_to_add)} 个 {ticker_type.value} 股票代码。"
            )
        else:
            logging.info(f"未能从 API 获取到 {ticker_type.value} 股票代码。")
