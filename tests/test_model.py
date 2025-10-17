import pytest
from sqlmodel import SQLModel, create_engine

from src.snipster.models import Item, create_items

engine = create_engine("sqlite:///:memory:", echo=True)


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    # create_db_and_tables()
    SQLModel.metadata.create_all(engine)


def test_create_items():
    item = Item(name="Laptop", price=999.99)
    create_items(item)

    assert item.name == "Laptop"
    assert item.price == 999.99


def test_alternate_constructor():
    params = {"name": "AlternateConstructor", "price": 56}

    snippet_class_method = Item.alternate_constructor(**params)

    create_items(snippet_class_method)
    assert snippet_class_method.name == "AlternateConstructor"
