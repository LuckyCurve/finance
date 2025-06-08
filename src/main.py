from db import engine
from db.common import Base

if __name__ == "__main__":
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
