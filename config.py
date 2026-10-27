"""Shared settings for ingest, retrieve and answer."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()  # reads .env into the environment; harmless if the file is missing

# Data and vector store
DATA_DIR = Path("data")
COLLECTION = "norvik_docs"
QDRANT_URL = "http://localhost:6333"

# Embeddings: ingest and retrieve MUST use the same model
EMBED_MODEL = "BAAI/bge-small-en-v1.5"  # 384-dim
EMBED_DEVICE = "mps"                     # use "cpu" if mps errors
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "

# Chunking
MAX_CHARS = 1500

# Retrieval
TOP_K = 10

# LLM (used from answer.py later)
LLM_MODEL = "claude-haiku-5-5"  # switch to claude-sonnet-5-5 to compare quality
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")  # None until you fill .env