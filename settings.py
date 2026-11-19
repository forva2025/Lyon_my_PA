"""Project settings. Change these values if you use different Ollama models."""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DOCUMENTS_DIR = DATA_DIR / "documents"
CHROMA_DIR = DATA_DIR / "chroma_db"

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
LLM_MODEL = os.getenv("RAG_LLM_MODEL", "qwen3:1.7b")
EMBEDDING_MODEL = os.getenv("RAG_EMBEDDING_MODEL", "nomic-embed-text")
COLLECTION_NAME = "local_knowledge_base"

# Conservative defaults for a Windows computer with 8 GB RAM.
CHUNK_SIZE = 1_000       # characters, not tokens
CHUNK_OVERLAP = 150      # characters
EMBED_BATCH_SIZE = 8
DEFAULT_TOP_K = 4
MAX_TOP_K = 6
NUM_CTX = 2_048
MAX_OUTPUT_TOKENS = 512
OLLAMA_TIMEOUT_SECONDS = 600
MAX_UPLOAD_MB = 50
