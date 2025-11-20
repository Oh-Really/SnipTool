import pytest
from sqlmodel import SQLModel, create_engine

from snipster.repo import DatabaseSnippetRepository, InMemorySnippetRepository


@pytest.fixture(scope="function")
def engine():
    engine = create_engine("sqlite:///:memory:", echo=False)
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def in_mem_repo():
    return InMemorySnippetRepository()


@pytest.fixture(scope="function")
def db_repo(engine):
    return DatabaseSnippetRepository(engine)
