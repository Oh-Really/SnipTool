import os

from dotenv import load_dotenv
from sqlmodel import Field, Session, SQLModel, create_engine, select


class Item(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    price: float

    @classmethod
    def alternate_constructor(cls, **kwargs):
        return cls(**kwargs)


load_dotenv()
engine = create_engine(os.environ["DB_URL"], echo=False)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def create_items(item):
    with Session(engine) as session:
        session.add(item)
        session.commit()
        session.refresh(item)


def select_items():
    with Session(engine) as session:
        statement = select(Item)
        results = session.exec(statement)
        for item in results:
            print(item)


def main():
    create_db_and_tables()
    # create_items()
    # select_items()


if __name__ == "__main__":
    main()
    print("Database + table created!")
