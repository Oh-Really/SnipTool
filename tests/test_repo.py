import pytest
from sqlmodel import Session, SQLModel, select

from src.snipster.models import Snippet, engine
from src.snipster.repo import DatabaseSnippetRepository, InMemorySnippetRepository


@pytest.fixture(scope="function")
def in_mem_repo():
    return InMemorySnippetRepository()


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


# def test_add_snippet():
#     snippet = Snippet(
#         title="Testing 1st Snippet", code="ABC", description="Test snippet 1"
#     )
#     repo = InMemorySnippetRepository()
#     repo.add(snippet)
#     assert repo._data[1].title == "Testing 1st Snippet"


def test_get_snippet(add_in_memory_snippet, in_mem_repo):
    item = in_mem_repo._data.get(1)
    assert item == add_in_memory_snippet


def test_list_snippet(add_in_memory_snippet, in_mem_repo):
    snippet_list = in_mem_repo.list()
    # assert snippet_list == list(add_snippet)
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


@pytest.fixture(scope="function")
def setup_db():
    # Create tables before each test
    SQLModel.metadata.create_all(engine)
    yield
    # Drop tables after each test to isolate data
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def db_repo(setup_db):
    return DatabaseSnippetRepository(engine)


@pytest.fixture(scope="function")
def add_db_snippet(db_repo):
    snippet = Snippet(
        title="Testing 1st Snippet", code="ABC", description="Test snippet 1"
    )
    db_repo.add(snippet)
    return snippet  # Why do I need to return the snippet object?


def test_db_add_snippet(db_repo):
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


def test_get_db_snippet(add_db_snippet, db_repo):
    result = db_repo.get(1)
    assert result is not None
    assert result.code == "ABC"


def test_list_db_snippet(add_db_snippet, db_repo):
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
