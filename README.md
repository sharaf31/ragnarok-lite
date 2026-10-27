# ragnarok-lite

A small, local RAG (retrieval-augmented generation) system built to understand the internals.
Documents are chunked by markdown heading, embedded locally, stored in Qdrant, and (soon) answered by Claude with citations.

```
INGEST:  data/*.md -> chunk by heading -> embed (bge-small) -> Qdrant
QUERY:   question  -> embed (+query prefix) -> top-k search -> prompt -> Claude -> answer + sources
```

## Stack
| Layer | Choice |
|---|---|
| Language | Python 3.12 |
| Embeddings | `BAAI/bge-small-en-v1.5` via `sentence-transformers` (local, 384-dim, Apple MPS) |
| Vector store | Qdrant (Docker) |
| LLM | Anthropic API (`claude-haiku-5-5` by default; set in `config.py`) |

## Project layout
```
ragnarok-lite/
├── config.py            # shared settings (paths, model names, top-k, LLM)
├── ingest.py            # load -> chunk -> embed -> upsert
├── retrieve.py          # embed query -> top-k search -> print hits
├── answer.py            # (planned) build prompt -> call Claude -> answer + sources
├── data/                # source documents (sample: fictional "Norvik Instruments" docs)
├── eval_questions.md    # test questions with expected answers
├── docker-compose.yml   # Qdrant
├── requirements.txt     # direct dependencies
├── .env.example         # ANTHROPIC_API_KEY=
└── .python-version      # 3.12
```

## Setup (macOS, Homebrew)
```bash
brew install python@3.12
git clone <this-repo> && cd ragnarok-lite

/opt/homebrew/bin/python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

docker compose up -d            # Qdrant at http://localhost:6333/dashboard
cp .env.example .env            # add ANTHROPIC_API_KEY (only needed for answer.py)
```

> Use Python 3.12. PyTorch has no wheels for the newest Python releases, so a newer interpreter fails at install time.

## Usage
```bash
# 1. Index the documents (rebuilds the collection each run)
python ingest.py
# expected: "37 chunks from 6 files" ... "Upserted 37 points into 'norvik_docs'"

# 2. Retrieve only (no API key needed)
python retrieve.py "What is the battery life of the Skylark Pro outdoor array?"
```

Run commands from the project root, since `data/` is a relative path.

## Design notes
- **Heading-based chunking.** Sections follow the markdown headings; oversized sections are split on blank lines so tables and Q&A blocks are never cut in half.
- **Heading path in the embedded text.** Each chunk is prefixed with e.g. `Manual > 4. Specifications`, so a bare table row stays findable.
- **Asymmetric embeddings.** BGE queries get an instruction prefix (`QUERY_PREFIX` in `config.py`); documents do not. Ingest and query must use the same model.
- **Deterministic point IDs.** `uuid5(source:chunk_index)`, so re-ingesting overwrites instead of duplicating.
- **Retrieval before generation.** `eval_questions.md` is meant to be run against `retrieve.py` first; check that the right chunk is in the top 5 before involving the LLM.

## Status
- [x] Qdrant via Docker
- [x] Ingestion (chunk, embed, upsert)
- [x] Retrieval with CLI
- [ ] Generation with citations (`answer.py`), preferring the newest source when documents conflict
- [ ] "Not found" handling for unanswerable questions
- [ ] Evaluation script over `eval_questions.md`

## Sample data
The documents in `data/` describe a fictional company and are for testing only.
