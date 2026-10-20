import json
from pathlib import Path

from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer


# Configuration
COLLECTION_NAME = "shadowtrace_bugs"
DATASET_PATH = Path(__file__).parent / "bugs.json"

# Initialize the embedding model
print("Loading embedding model...")

model = SentenceTransformer("all-MiniLM-L6-v2")

# Initialize local Qdrant storage
storage_path = Path(__file__).parent / "qdrant_storage"
client = QdrantClient(path=str(storage_path))


def load_bugs():
    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def initialize_database():
    bugs = load_bugs()

    # Create the collection if it doesn't exist
    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=model.get_sentence_embedding_dimension(),
                distance=models.Distance.COSINE,
            ),
        )

    # Create payload indexes for filtering
    collection_info = client.get_collection(COLLECTION_NAME)

    if collection_info.points_count == 0:
        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="language",
            field_schema=models.PayloadSchemaType.KEYWORD,
        )

        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="category",
            field_schema=models.PayloadSchemaType.KEYWORD,
        )

        # Convert bug descriptions into vectors
        texts = [
            f"{bug['title']}. {bug['description']}. "
            f"Root cause: {bug['root_cause']}. "
            f"Solution: {bug['solution']}"
            for bug in bugs
        ]

        vectors = model.encode(texts, normalize_embeddings=True)

        points = [
            models.PointStruct(
                id=bug["id"],
                vector=vector.tolist(),
                payload=bug,
            )
            for bug, vector in zip(bugs, vectors)
        ]

        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points,
        )

    print(f"Database initialized with {len(bugs)} sample bugs.")


def search_bugs(query, language="All Languages", limit=5):
    query_vector = model.encode(
        query,
        normalize_embeddings=True,
    ).tolist()

    search_filter = None

    if language != "All Languages":
        search_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="language",
                    match=models.MatchValue(value=language),
                )
            ]
        )

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        query_filter=search_filter,
        limit=limit,
        with_payload=True,
    ).points

    return [
        {
            **result.payload,
            "score": round(result.score, 4),
        }
        for result in results
    ]


if __name__ == "__main__":
    initialize_database()

    while True:
        query = input("\nDescribe your programming error (or 'exit'): ")

        if query.lower() == "exit":
            break

        language = input(
            "Language (All Languages, Java, Python, C, C++): "
        )

        if not language.strip():
            language = "All Languages"

        matches = search_bugs(query, language)

        print("\n--- Matching Bugs ---")

        if not matches:
            print("No matching records found.")
            continue

        for bug in matches:
            print(f"\n{bug['title']} ({bug['language']})")
            print(f"Similarity score: {bug['score']}")
            print(f"Cause: {bug['root_cause']}")
            print(f"Solution: {bug['solution']}")