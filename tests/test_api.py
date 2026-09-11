import pytest
from fastapi.testclient import TestClient

from snipster.api import app, get_repo


@pytest.fixture()
def client(db_repo):
    app.dependency_overrides[get_repo] = lambda: db_repo

    test_client = TestClient(app)
    yield test_client

    app.dependency_overrides.clear()


def test_create_snippet(client):
    payload = {
        "title": "API Test Snippet",
        "code": "print('Hello API')",
        "description": "Test description",
    }

    response = client.post("/snippets/", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["title"] == payload["title"]
    assert data["code"] == payload["code"]
    assert data["description"] == payload["description"]
    assert "id" in data
