import pytest
from fastapi.testclient import TestClient

from snipster.api import app, get_repo
from snipster.repo import InMemorySnippetRepository


@pytest.fixture(name="client")
def client_fixture():
    memory_repo = InMemorySnippetRepository()
    app.dependency_overrides[get_repo] = lambda: memory_repo

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def created_snippet(client: TestClient):
    payload = {
        "title": "API Test Snippet",
        "code": "print('Hello API')",
        "description": "Test description",
    }

    response = client.post("/snippets/", json=payload)
    assert response.status_code == 200

    return response.json()


def test_get_snippet__via_id(client, created_snippet):
    snippet_id = created_snippet["id"]

    response = client.get(f"/snippets/{snippet_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == snippet_id
    assert data["title"] == created_snippet["title"]


def test_get_snippet_list(client, created_snippet):
    resp = client.get("/snippets/")
    assert resp.status_code == 200

    data = resp.json()
    assert isinstance(data, list)
    assert any(snippet["id"] == created_snippet["id"] for snippet in data)


def test_delete_snippet(client, created_snippet):
    snippet_id = created_snippet["id"]
    delete_response = client.delete(f"snippets/{snippet_id}")
    assert delete_response.status_code == 200

    resp = client.get(f"/snippets/{snippet_id}")
    assert resp.status_code == 404


def test_delete_snippet_not_found_returns_404(client):
    resp = client.delete("/snippets/9999")
    assert resp.status_code == 404
