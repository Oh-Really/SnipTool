import pytest
from sqlmodel import Session, SQLModel, create_engine

from snipster.models import Snippet

engine = create_engine("sqlite:///:memory:", echo=True)


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    SQLModel.metadata.create_all(engine)


def test_create_items():
    snippet = Snippet(title="Hello World", code="Print('Hello World!')")
    with Session(engine) as session:
        session.add(snippet)
        session.commit()
        session.refresh(snippet)

    assert snippet.title == "Hello World"
    assert snippet.code == "Print('Hello World!')"


def test_alternate_constructor():
    params = {"title": "AlternateConstructor", "code": "Print('Alternate constructor')"}

    snippet_class_method = Snippet.alternate_constructor(**params)

    with Session(engine) as session:
        session.add(snippet_class_method)
        session.commit()
        session.refresh(snippet_class_method)
    assert snippet_class_method.title == "AlternateConstructor"
