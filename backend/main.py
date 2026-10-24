from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from search_engine import (
    initialize_database,
    search_bugs,
    get_all_bugs,
    add_bug,
    update_bug,
    delete_bug,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="ShadowTrace API",
    description="Semantic bug search powered by Qdrant",
    version="1.0.0",
    lifespan=lifespan,
)


# Allow requests from the React development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type"],
)


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    language: str = "All Languages"
    limit: int = Field(default=5, ge=1, le=10)

class BugCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=2000)
    root_cause: str = Field(min_length=1, max_length=2000)
    solution: str = Field(min_length=1, max_length=2000)
    language: str = Field(min_length=1, max_length=50)
    category: str = Field(min_length=1, max_length=100)
    buggy_code: str = Field(min_length=1, max_length=5000)
    fixed_code: str = Field(min_length=1, max_length=5000)


@app.get("/")
def home():
    return {
        "message": "Welcome to ShadowTrace API",
        "status": "running",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/api/bugs")
def list_bugs():
    try:
        bugs = get_all_bugs()

        return {
            "count": len(bugs),
            "bugs": bugs,
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve bug records.",
        ) from error


@app.get("/api/bugs/{bug_id}")
def get_bug(bug_id: int):
    try:
        bugs = get_all_bugs()

        for bug in bugs:
            if bug["id"] == bug_id:
                return bug

        raise HTTPException(
            status_code=404,
            detail=f"Bug with ID {bug_id} not found.",
        )

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve the bug record.",
        ) from error


@app.post("/api/bugs", status_code=201)
def create_bug(request: BugCreate):
    try:
        bugs = get_all_bugs()

        new_id = max(
            (bug["id"] for bug in bugs),
            default=0,
        ) + 1

        bug = {
            "id": new_id,
            **request.model_dump(),
        }

        add_bug(bug)

        return {
            "message": "Bug created successfully.",
            "bug": bug,
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Unable to create the bug record.",
        ) from error


@app.put("/api/bugs/{bug_id}")
def edit_bug(bug_id: int, request: BugCreate):
    try:
        updated_data = request.model_dump()

        bug = update_bug(
            bug_id=bug_id,
            updated_data=updated_data,
        )

        if bug is None:
            raise HTTPException(
                status_code=404,
                detail=f"Bug with ID {bug_id} not found.",
            )

        return {
            "message": "Bug updated successfully.",
            "bug": bug,
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Unable to update the bug record.",
        ) from error

@app.delete("/api/bugs/{bug_id}")
def remove_bug(bug_id: int):
    try:
        deleted = delete_bug(bug_id)

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail=f"Bug with ID {bug_id} not found.",
            )

        return {
            "message": f"Bug with ID {bug_id} deleted successfully."
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Unable to delete the bug record.",
        ) from error
    

@app.post("/api/search")
def search(request: SearchRequest):
    query = request.query.strip()

    if not query:
        raise HTTPException(
            status_code=422,
            detail="Please enter a programming error to search.",
        )

    allowed_languages = {
        "All Languages",
        "Java",
        "Python",
        "C",
        "C++",
        "JavaScript",
    }

    if request.language not in allowed_languages:
        raise HTTPException(
            status_code=422,
            detail="Unsupported programming language.",
        )

    try:
        results = search_bugs(
            query=query,
            language=request.language,
            limit=request.limit,
        )

        return {
            "query": query,
            "language": request.language,
            "count": len(results),
            "results": results,
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="An error occurred while searching the bug database.",
        ) from error