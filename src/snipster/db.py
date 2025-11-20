from sqlmodel import SQLModel, create_engine


def get_engine(db_url: str, echo: bool = False):
    return create_engine(db_url, echo=echo)


def create_db_and_tables(engine):
    SQLModel.metadata.create_all(engine)
