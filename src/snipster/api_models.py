from sqlmodel import SQLModel


class SnippetBase(SQLModel):
    title: str
    code: str
    description: str | None = None
    favourite: bool = False


class SnippetCreate(SnippetBase):
    pass


class SnippetRead(SnippetBase):
    id: int


class SnippetUpdate(SnippetBase):
    title: str
    code: str
    description: str | None
    favourite: bool
