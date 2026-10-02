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
