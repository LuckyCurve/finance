import service
import service.sync

if __name__ == "__main__":
    # Base.metadata.drop_all(db.engine)
    # Base.metadata.create_all(db.engine)

    service.sync.sync_exchange_rate()
