import db
from db.common import Base
from service.sync import sync_asset, sync_exchange_rate, sync_ticker_info

if __name__ == "__main__":
    Base.metadata.create_all(db.engine)
    sync_exchange_rate()
    sync_asset()
    sync_ticker_info()


def sync():
    pass
    # buy_stock("GOOGL", date(2025, 6, 11), 1.8184, 154.17)
    # buy_stock("IAU", date(2025, 6, 11), 4.5126, 55.48)
    # buy_stock("SPLG", date(2025, 6, 11), 30.5197, 64.02)
    # buy_stock("GGB", date(2025, 6, 11), 338.9833, 2.95)
    # buy_stock("BIDU", date(2025, 6, 11), 15.3333, 84.57)
    # buy_stock("QQQM", date(2025, 6, 11), 4.6773, 213.87)
    # buy_stock("SGOV", date(2025, 6, 11), 222.4285, 100.49)
    # buy_stock("PDD", date(2025, 6, 11), 0.8267, 121.38)
