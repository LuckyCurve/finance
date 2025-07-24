from sqlalchemy import Engine, create_engine

engine: Engine = create_engine("sqlite:///data/finance.db")
