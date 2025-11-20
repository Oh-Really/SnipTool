from sqlmodel import Field, SQLModel


class Snippet(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    code: str
    description: str | None = None
    favourite: bool = False

    @classmethod
    def alternate_constructor(cls, **kwargs):
        return cls(**kwargs)


# engine = create_engine(config("DB_URL"), echo=False)


# def create_db_and_tables():
#     SQLModel.metadata.create_all(engine)


# def create_items(item):
#     with Session(engine) as session:
#         session.add(item)
#         session.commit()
#         session.refresh(item)


# def select_items():
#     with Session(engine) as session:
#         statement = select(Snippet)
#         results = session.exec(statement)
#         for item in results:
#             print(item)


# def main():
#     create_db_and_tables()
#     # create_items()
#     # select_items()


# if __name__ == "__main__":
#     main()
#     print("Database + table created!")
