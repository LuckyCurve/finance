from datetime import date

from akshare import stock_hk_hist, stock_hk_spot_em, stock_us_hist, stock_us_spot_em


def get_all_us_symbols() -> list[tuple[str, str]]:
    df = stock_us_spot_em()
    return [(row["名称"], row["代码"]) for _, row in df.iterrows()]


def get_us_ticker_history(
    symbol: str, start_date: date, end_date: date
) -> list[tuple[date, float]]:
    df = stock_us_hist(
        symbol=symbol,
        period="daily",
        start_date=start_date.strftime("%Y%m%d"),
        end_date=end_date.strftime("%Y%m%d"),
    )
    return [(date.fromisoformat(row["日期"]), row["收盘"]) for _, row in df.iterrows()]


def get_all_hk_symbols() -> list[tuple[str, str]]:
    df = stock_hk_spot_em()
    return [(row["名称"], row["代码"]) for _, row in df.iterrows()]


def get_hk_ticker_history(
    symbol: str, start_date: date, end_date: date
) -> list[tuple[date, float]]:
    df = stock_hk_hist(
        symbol=symbol,
        period="daily",
        start_date=start_date.strftime("%Y%m%d"),
        end_date=end_date.strftime("%Y%m%d"),
    )
    return [(row["日期"], row["收盘"]) for _, row in df.iterrows()]
