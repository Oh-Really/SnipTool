import pytest

from src.snipster.models import Snippet
from src.snipster.repo import InMemorySnippetRepository


@pytest.fixture(scope="function")
def in_mem_repo():
    return InMemorySnippetRepository()


# @pytest.fixture(scope="function")
# def add_snippet():
#     snippet = Snippet(
#         title = "Testing 1st Snippet",
#         code = "ABC",
#         description = "Test snippet 1"
#     )


def test_add_snippet(in_mem_repo):
    snippet = Snippet(
        title="Testing 1st Snippet", code="ABC", description="Test snippet 1"
    )

    # repo = InMemorySnippetRepository()

    in_mem_repo.add(snippet)
    assert in_mem_repo._data[1] == snippet
