from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from search_engine import initialize_database, search_bugs


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
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    language: str = "All Languages"
    limit: int = Field(default=5, ge=1, le=10)


@app.get("/")
def home():
    return {
        "message": "Welcome to ShadowTrace API",
        "status": "running",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


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