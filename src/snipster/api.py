from decouple import config
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import SQLModel

from snipster.api_models import SnippetCreate, SnippetRead, SnippetUpdate
from snipster.db import get_engine
from snipster.exceptions import SnippetNotFoundError
from snipster.models import Snippet
from snipster.repo import DatabaseSnippetRepository

app = FastAPI()

DB_URL = config("DB_URL")


def get_repo():
    engine = get_engine(DB_URL)
    SQLModel.metadata.create_all(engine)
    return DatabaseSnippetRepository(engine)


@app.post("/snippets/", response_model=SnippetRead)
def create_snippet(snippet: SnippetCreate, repo=Depends(get_repo)):
    db_snippet = Snippet.model_validate(snippet)
    repo.add(db_snippet)
    return db_snippet


@app.get("/snippets/", response_model=list[SnippetRead])
def list_snippets(repo=Depends(get_repo)):
    return repo.list()


@app.get("/snippets/{snippet_id}", response_model=SnippetRead)
def get_snippet(snippet_id: int, repo=Depends(get_repo)):
    snippet = repo.get(snippet_id)
    if not snippet:
        raise HTTPException(status_code=404, detail=f"Snippet {snippet_id} not found")
    return snippet


@app.delete("/snippets/{snippet_id}")
def delete_snippet(snippet_id: int, repo=Depends(get_repo)):
    try:
        repo.delete(snippet_id)
        return {"message": f"Snippet {snippet_id} deleted"}
    except SnippetNotFoundError:
        raise HTTPException(status_code=404, detail=f"Snippet {snippet_id} not found")


@app.patch("/snippets/{snippet_id}", response_model=SnippetRead)
def update_snippet(snippet_id: int, snippet: SnippetUpdate, repo=Depends(get_repo)):
    db_snippet = repo.get(snippet_id)
    if not db_snippet:
        raise HTTPException(status_code=404, detail=f"Snippet {snippet_id} not found")

    updated_data = snippet.model_dump(exclude_unset=True)
    for field, value in updated_data.items():
        setattr(db_snippet, field, value)

    updated_snippet = repo.update(snippet_id, updated_data)
    return updated_snippet


@app.get("/snippets/search", response_model=list[SnippetRead])
def search_snippets(
    search_string: str = Query(..., min_length=1), repo=Depends(get_repo)
):
    return repo.search(search_string)


@app.post("/snippets/{snippet_id}/favourite", response_model=SnippetRead)
def toggle_favourite(snippet_id: int, repo=Depends(get_repo)):
    try:
        repo.favourite(snippet_id)
    except SnippetNotFoundError:
        raise HTTPException(status_code=404, detail="Snippet not found")
    return repo.get(snippet_id)
