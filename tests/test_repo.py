import pytest
from sqlmodel import Session, select

from snipster.models import Snippet


@pytest.fixture(scope="function")
def add_in_memory_snippet(in_mem_repo):
    snippet = Snippet(
        title="Testing 1st Snippet", code="ABC", description="Test snippet 1"
    )
    in_mem_repo.add(snippet)
    return snippet
    # Should this not be return in_mem_repo?


def test_add_snippet(add_in_memory_snippet, in_mem_repo):
    assert in_mem_repo._data[1].title == "Testing 1st Snippet"


def test_get_snippet(add_in_memory_snippet, in_mem_repo):
    item = in_mem_repo._data.get(1)
    assert item == add_in_memory_snippet


def test_list_snippet(add_in_memory_snippet, in_mem_repo):
    snippet_list = in_mem_repo.list()
    assert len(snippet_list) == 1


def test_delete(add_in_memory_snippet, in_mem_repo):
    in_mem_repo.delete(1)
    assert in_mem_repo._data.get(1) is None


def test_update_snippet(add_in_memory_snippet, in_mem_repo):
    snippet = in_mem_repo._data.get(1)
    assert snippet.title == "Testing 1st Snippet"
    updated_snippet = snippet.model_copy()
    updated_snippet.title = "Updated snippet"
    snippet = in_mem_repo.update(snippet.id, updated_snippet)
    assert snippet.title == "Updated snippet"


def test_favourite_snippet(add_in_memory_snippet, in_mem_repo):
    snippet = in_mem_repo._data.get(1)
    print(snippet.favourite)
    assert not snippet.favourite
    in_mem_repo.favourite(1)
    snippet = in_mem_repo._data.get(1)
    assert snippet.favourite
    in_mem_repo.favourite(1)
    snippet = in_mem_repo._data.get(1)
    assert not snippet.favourite
    # Will this work if I create a snippet that is favourited by default??


@pytest.fixture(scope="function")
def add_db_snippet(db_repo):
    snippet = Snippet(
        title="Testing 1st Snippet", code="ABC", description="Test snippet 1"
    )
    db_repo.add(snippet)
    return snippet  # Why do I need to return the snippet object?


def test_add_db_snippet(db_repo):
    snippet = Snippet(
        title="Testing DB Snippet", code="XYZ", description="DB snippet test"
    )

    db_repo.add(snippet)

    with Session(db_repo.engine) as session:
        statement = select(Snippet).where(Snippet.title == "Testing DB Snippet")
        result = session.exec(statement).first()

        assert result is not None
        assert result.code == "XYZ"
        assert result.description == "DB snippet test"


def test_get_snippet_db(add_db_snippet, db_repo):
    result = db_repo.get(1)
    assert result is not None
    assert result.code == "ABC"


def test_list_snippet_db(add_db_snippet, db_repo):
    result = db_repo.list()
    assert len(result) == 1
    assert result[0].title == "Testing 1st Snippet"


def test_delete_snippet_db(add_db_snippet, db_repo):
    repo = db_repo
    snippet = repo.list()[0]
    repo.delete(snippet.id)

    with Session(repo.engine) as session:
        result = session.exec(select(Snippet).where(Snippet.id == snippet.id)).first()
        assert result is None


def test_update_snippet_db(add_db_snippet, db_repo):
    repo = db_repo
    snippet = repo.list()[0]
    updated = Snippet(title="Updated", code="XYZ", description="Updated desc")
    repo.update(snippet.id, updated)

    with Session(repo.engine) as session:
        result = session.exec(select(Snippet).where(Snippet.id == snippet.id)).first()
        assert result.title == "Updated"
        assert result.code == "XYZ"


def test_favourite_snippet_db(add_db_snippet, db_repo):
    snippet = db_repo.get(1)
    assert not snippet.favourite
    db_repo.favourite(1)
    snippet = db_repo.get(1)
    assert snippet.favourite
    db_repo.favourite(1)
    snippet = db_repo.get(1)
    assert not snippet.favourite


@pytest.mark.parametrize("repo_fixture", ["in_mem_repo", "db_repo"])
def test_search_snippets(repo_fixture, request):
    repo = request.getfixturevalue(repo_fixture)

    s1 = Snippet(
        title="Hello World", code="print('Hello')", description="A test snippet"
    )
    s2 = Snippet(title="Quick Sort", code="...", description="Algorithm")
    s3 = Snippet(title="HELLO AGAIN", code="print('Again')", description="Greeting")

    repo.add(s1)
    repo.add(s2)
    repo.add(s3)
    results = repo.search("hello")

    assert len(results) == 2
    titles = [s.title for s in results]
    assert "Hello World" in titles
