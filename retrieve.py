import sys

from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

from config import EMBED_DEVICE, EMBED_MODEL, QDRANT_URL, QUERY_PREFIX, COLLECTION, TOP_K

def embed_query(query: str, model: SentenceTransformer) -> list[float]:
    vec = model.encode(QUERY_PREFIX + query, normalize_embeddings=True)
    return vec.tolist()

def search(query: str, model: SentenceTransformer, client: QdrantClient, k: int = TOP_K) -> list[dict]:
    vector = embed_query(query, model)
    response = client.query_points(
        collection_name=COLLECTION,
        query=vector,
        limit=k,
        with_payload=True,
    )
    return [
        {
            "score": p.score,
            "source": p.payload["source"],
            "heading_path": p.payload["heading_path"],
            "text": p.payload["text"],
        }
        for p in response.points
    ]
def print_hits(hits: list[dict]) -> None:
    for rank, h in enumerate(hits, start=1):
        snippet = h["text"][:200].replace("\n", " ")
        print(f"{rank}. [{h['score']:.3f}] {h['source']}")
        print(f"   {h['heading_path']}")
        print(f"   {snippet}...")
        print()

def main() -> None:
    if len(sys.argv) < 2:
        print('Usage: python retrieve.py "your question"')
        sys.exit(1)
    question = " ".join(sys.argv[1:])

    model = SentenceTransformer(EMBED_MODEL, device=EMBED_DEVICE)
    client = QdrantClient(url=QDRANT_URL)

    hits = search(question, model, client, k=TOP_K)
    print_hits(hits)


if __name__ == "__main__":
    main()