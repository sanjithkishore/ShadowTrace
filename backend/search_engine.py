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

    # Create payload indexes if they don't already exist
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

    # Retrieve existing bug IDs from Qdrant
    existing_ids = set()
    offset = None

    while True:
        records, next_offset = client.scroll(
            collection_name=COLLECTION_NAME,
            limit=100,
            offset=offset,
            with_payload=False,
            with_vectors=False,
        )

        existing_ids.update(record.id for record in records)

        if next_offset is None:
            break

        offset = next_offset

    # Identify bugs that are new or have changed
    bugs_to_sync = []

    for bug in bugs:
        if bug["id"] not in existing_ids:
            bugs_to_sync.append(bug)
            continue

        stored_records = client.retrieve(
            collection_name=COLLECTION_NAME,
            ids=[bug["id"]],
            with_payload=True,
            with_vectors=False,
        )

        if not stored_records or any(
            stored_records[0].payload.get(key) != value
            for key, value in bug.items()
        ):
            bugs_to_sync.append(bug)

    # Generate embeddings and synchronize changed records
    if bugs_to_sync:
        texts = [
            f"{bug['title']}. {bug['description']}. "
            f"Root cause: {bug['root_cause']}. "
            f"Solution: {bug['solution']}"
            for bug in bugs_to_sync
        ]

        vectors = model.encode(texts, normalize_embeddings=True)

        points = [
            models.PointStruct(
                id=bug["id"],
                vector=vector.tolist(),
                payload=bug,
            )
            for bug, vector in zip(bugs_to_sync, vectors)
        ]

        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points,
        )

    print(
        f"Database synchronized: {len(bugs)} bugs in the dataset; "
        f"{len(bugs_to_sync)} inserted or updated."
    )

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