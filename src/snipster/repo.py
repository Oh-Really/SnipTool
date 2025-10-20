from abc import ABC, abstractmethod
from typing import Sequence

from .exceptions import SnippetNotFoundError
from .models import Snippet


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


class InMemorySnippetRepository(SnippetRepository):
    def __init__(self) -> None:
        self._data: dict[int, Snippet] = {}

    def add(self, snippet: Snippet) -> None:
        next_id = max(self._data.keys(), default=0) + 1
        self._data[next_id] = snippet
        return self._data

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
        return self._data


class DatabaseSnippetRepository(SnippetRepository):
    pass
