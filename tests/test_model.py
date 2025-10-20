import pytest
from sqlmodel import SQLModel, create_engine

from src.snipster.models import Snippet, create_items

engine = create_engine("sqlite:///:memory:", echo=True)


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    # create_db_and_tables()
    SQLModel.metadata.create_all(engine)


def test_create_items():
    snippet = Snippet(title="Hello World", code="Print('Hello World!')")
    create_items(snippet)

    assert snippet.title == "Hello World"
    assert snippet.code == "Print('Hello World!')"


def test_alternate_constructor():
    params = {"title": "AlternateConstructor", "code": "Print('Alternate constructor')"}

    snippet_class_method = Snippet.alternate_constructor(**params)

    create_items(snippet_class_method)
    assert snippet_class_method.title == "AlternateConstructor"
