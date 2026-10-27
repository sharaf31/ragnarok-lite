"""Ingest markdown docs into Qdrant: load -> chunk by heading -> embed -> upsert."""
import re
import uuid
from pathlib import Path

DATA_DIR = Path("data")
COLLECTION = "norvik_docs"
MODEL_NAME = "BAAI/bge-small-en-v1.5"  # 384-dim
QDRANT_URL = "http://localhost:6333"
MAX_CHARS = 1500  # ~375 tokens; sections longer than this are split on blank lines
NAMESPACE = uuid.UUID("6f1c2f0e-8f6a-4a52-9d3e-5b7c1a2d4e90")  # fixed => stable IDs

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")


def split_sections(text: str) -> list[tuple[str, str]]:
    """Return [(heading_path, body)] using markdown headings as boundaries."""
    stack: list[tuple[int, str]] = []  # (level, title)
    sections: list[tuple[str, str]] = []
    buf: list[str] = []

    def flush():
        body = "\n".join(buf).strip()
        if body and body != "---":
            sections.append((" > ".join(t for _, t in stack), body))
        buf.clear()

    for line in text.splitlines():
        m = HEADING_RE.match(line)
        if m:
            flush()
            level, title = len(m.group(1)), m.group(2)
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, title))
        else:
            buf.append(line)
    flush()
    return sections


def pack_paragraphs(body: str, max_chars: int) -> list[str]:
    """Greedily pack blank-line-separated blocks (tables/lists stay intact) up to max_chars."""
    if len(body) <= max_chars:
        return [body]
    chunks, cur = [], ""
    for block in re.split(r"\n\s*\n", body):
        block = block.strip()
        if not block:
            continue
        if cur and len(cur) + len(block) + 2 > max_chars:
            chunks.append(cur)
            cur = block
        else:
            cur = f"{cur}\n\n{block}" if cur else block
    if cur:
        chunks.append(cur)
    return chunks


def chunk_file(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    out: list[dict] = []
    for heading_path, body in split_sections(text):
        for piece in pack_paragraphs(body, MAX_CHARS):
            out.append(
                {
                    "source": path.name,
                    "heading_path": heading_path,
                    # prefix the heading path so the embedding carries its context
                    "text": f"{heading_path}\n\n{piece}",
                }
            )
    for i, c in enumerate(out):
        c["chunk_index"] = i
    return out


def main() -> None:
    # heavy imports here so chunking can be tested without them
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, PointStruct, VectorParams
    from sentence_transformers import SentenceTransformer

    chunks: list[dict] = []
    for p in sorted(DATA_DIR.glob("*.md")):
        chunks.extend(chunk_file(p))
    print(f"{len(chunks)} chunks from {len(list(DATA_DIR.glob('*.md')))} files")

    model = SentenceTransformer(MODEL_NAME, device="mps")  # use "cpu" if mps fails
    # NOTE: documents get NO query prefix; only queries do (see retrieve.py)
    vectors = model.encode(
        [c["text"] for c in chunks],
        normalize_embeddings=True,
        batch_size=32,
        show_progress_bar=True,
    )

    client = QdrantClient(url=QDRANT_URL)
    # simple and safe for a tutorial: rebuild the collection on every run
    if client.collection_exists(COLLECTION):
        client.delete_collection(COLLECTION)
    client.create_collection(
        COLLECTION,
        vectors_config=VectorParams(size=vectors.shape[1], distance=Distance.COSINE),
    )

    points = [
        PointStruct(
            id=str(uuid.uuid5(NAMESPACE, f"{c['source']}:{c['chunk_index']}")),
            vector=v.tolist(),
            payload=c,
        )
        for c, v in zip(chunks, vectors)
    ]
    client.upsert(COLLECTION, points=points)
    print(f"Upserted {len(points)} points into '{COLLECTION}'")


if __name__ == "__main__":
    main()