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


def test_update_snippet(client, created_snippet):
    snippet_id = created_snippet["id"]

    response = client.patch(f"/snippets/{snippet_id}", json={"title": "Updated Title"})
    assert response.status_code == 200

    data = response.json()
    assert data["title"] == "Updated Title"
    # fields not included in the payload should be untouched
    assert data["code"] == created_snippet["code"]
    assert data["description"] == created_snippet["description"]

    # persisted, not just returned
    get_response = client.get(f"/snippets/{snippet_id}")
    assert get_response.json()["title"] == "Updated Title"


def test_update_snippet_not_found_returns_404(client):
    response = client.patch("/snippets/9999", json={"title": "Doesn't matter"})
    assert response.status_code == 404


def test_search_snippets_finds_case_insensitive_title_match(client):
    client.post("/snippets/", json={"title": "Hello World", "code": "print('hi')"})
    client.post("/snippets/", json={"title": "Quick Sort", "code": "..."})
    client.post("/snippets/", json={"title": "HELLO AGAIN", "code": "print('again')"})

    response = client.get("/snippets/search", params={"search_string": "hello"})
    assert response.status_code == 200

    titles = [s["title"] for s in response.json()]
    assert "Hello World" in titles
    assert "HELLO AGAIN" in titles
    assert "Quick Sort" not in titles


def test_search_snippets_no_match_returns_empty_list(client, created_snippet):
    response = client.get("/snippets/search", params={"search_string": "doesnotexist"})
    assert response.status_code == 200
    assert response.json() == []


def test_toggle_favourite(client, created_snippet):
    snippet_id = created_snippet["id"]
    assert created_snippet["favourite"] is False

    response = client.post(f"/snippets/{snippet_id}/favourite")
    assert response.status_code == 200
    assert response.json()["favourite"] is True

    response = client.post(f"/snippets/{snippet_id}/favourite")
    assert response.status_code == 200
    assert response.json()["favourite"] is False


def test_toggle_favourite_not_found_returns_404(client):
    response = client.post("/snippets/9999/favourite")
    assert response.status_code == 404
