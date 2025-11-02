from abc import ABC, abstractmethod
from typing import Sequence

from sqlmodel import Session, select

from .exceptions import SnippetNotFoundError
from .models import Snippet  # , engine


class SnippetRepository(ABC):
    @abstractmethod
    def add(self, snippet: Snippet) -> None:
        pass

    @abstractmethod
    def get(self, snipped_id: int) -> Snippet | None:
        pass

    @abstractmethod
    def list(self) -> Sequence[Snippet]:
        pass

    @abstractmethod
    def delete(self, snippet_id: int) -> None:
        pass

    @abstractmethod
    def update(self, snippet_id: int) -> None:
        pass

    @abstractmethod
    def favourite(self, snippet_id: int) -> None:
        pass


class InMemorySnippetRepository(SnippetRepository):
    def __init__(self) -> None:
        self._data: dict[int, Snippet] = {}

    def add(self, snippet: Snippet) -> None:
        next_id = max(self._data.keys(), default=0) + 1
        self._data[next_id] = snippet
        # return self._data

    def get(self, snippet_id: int) -> Snippet | None:
        return self._data.get(snippet_id)

    def list(self) -> Sequence[Snippet]:
        return list(self._data.values())

    def delete(self, snippet_id: int) -> None:
        if snippet_id not in self._data:
            raise SnippetNotFoundError(f"Snippet with id {snippet_id} not found")
        self._data.pop(snippet_id)
        return self._data

    def update(self, snippet_id: int, updated_snippet: Snippet) -> None:
        self._data[snippet_id] = updated_snippet
        return self._data[snippet_id]

    def favourite(self, snippet_id: int) -> None:
        snippet = self._data.get(snippet_id)
        snippet.favourite = not snippet.favourite
        self.update(snippet_id, snippet)


class DatabaseSnippetRepository(SnippetRepository):
    def __init__(self, engine):
        self.engine = engine

    def add(self, snippet: Snippet) -> None:
        with Session(self.engine) as session:
            session.add(snippet)
            session.commit()
            session.refresh(snippet)
        # return snippet

    def get(self, snippet_id: int) -> Snippet | None:
        with Session(self.engine) as session:
            statement = select(Snippet).where(Snippet.id == snippet_id)
            result = session.exec(statement).first()
            return result

    def list(self) -> Snippet:
        with Session(self.engine) as session:
            statement = select(Snippet)
            result = session.exec(statement).all()
            return result

    def delete(self, snippet_id: int) -> None:
        with Session(self.engine) as session:
            statement = select(Snippet).where(Snippet.id == snippet_id)
            snip_to_delete = session.exec(statement).first()
            if not snip_to_delete:
                raise SnippetNotFoundError(f"Snippet with id {snippet_id} not found")

            session.delete(snip_to_delete)
            session.commit()

    def update(self, snippet_id: int, updated_snippet: Snippet) -> None:
        with Session(self.engine) as session:
            statement = select(Snippet).where(Snippet.id == snippet_id)
            snippet = session.exec(statement).first()

            if snippet is None:
                raise SnippetNotFoundError(f"Snippet with id {snippet_id} not found")

            snippet.title = updated_snippet.title
            snippet.code = updated_snippet.code
            snippet.description = updated_snippet.description
            snippet.favourite = updated_snippet.favourite

            session.add(snippet)
            session.commit()
            session.refresh(snippet)

            return snippet

    def favourite(self, snippet_id):
        snippet = self.get(snippet_id)
        snippet.favourite = not snippet.favourite
        self.update(snippet_id, snippet)
