"""Path constants."""

from os import getenv
from pathlib import Path

# Document directory resolution:
#   1. DOCUMENTS_DIR environment variable
#   2. /documents if it exists (Railway volume mount)
#   3. ./documents fallback (local development)
_env_dir = getenv("DOCUMENTS_DIR")
if _env_dir:
    DOCUMENTS_DIR = Path(_env_dir)
elif Path("/documents").is_dir():
    DOCUMENTS_DIR = Path("/documents")
else:
    DOCUMENTS_DIR = Path(__file__).resolve().parent.parent / "documents"

# Scout package paths
SCOUT_DIR = Path(__file__).parent
KNOWLEDGE_DIR = SCOUT_DIR / "knowledge"
SOURCES_DIR = KNOWLEDGE_DIR / "sources"
ROUTING_DIR = KNOWLEDGE_DIR / "routing"
PATTERNS_DIR = KNOWLEDGE_DIR / "patterns"
