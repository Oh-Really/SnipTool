from decouple import config
from fastapi import Depends, FastAPI

from snipster.api_models import SnippetCreate, SnippetRead
from snipster.db import get_engine
from snipster.models import Snippet
from snipster.repo import DatabaseSnippetRepository

app = FastAPI()

DB_URL = config("DB_URL")


def get_repo():
    engine = get_engine(DB_URL)
    return DatabaseSnippetRepository(engine)


@app.post("/snippets/", response_model=SnippetRead)
def create_snippet(snippet: SnippetCreate, repo=Depends(get_repo)):
    db_snippet = Snippet.model_validate(snippet)
    repo.add(db_snippet)
    return snippet


@app.get("/snippets/", response_model=list[SnippetRead])
def list_snippets(repo=Depends(get_repo)):
    return repo.list()


@app.get("/snippets/{snippet_id}", response_model=SnippetRead)
def get_snippet(snippet_id: int, repo=Depends(get_repo)):
    return repo.get(snippet_id)


@app.delete("/snippets/{snippet_id}")
def delete_snippet(snippet_id: int, repo=Depends(get_repo)):
    repo.delete(snippet_id)
    return {"message": f"Snippet {snippet_id} deleted"}
