"""
Backward-compatibility root entrypoint shim re-exporting core infrastructure and domain services.
"""

import sys
from src.shared.regex import *
from src.shared.security import *
from src.core.domain.models import *
from src.core.domain.services import *
from src.infrastructure.ocr import *
from src.infrastructure.parsers import *
from src.infrastructure.watcher import *
from src.infrastructure.llm import *
from src.infrastructure.database import *
import src.infrastructure.database as _infra_db
from src.domain.rag_engine import (
    generate_hyde_expansion,
    rrf_rerank,
    jaccard_deduplicate,
    extract_advanced_rag_context,
    decompose_multihop_query,
    precision_cross_rerank,
    parse_metadata_filters,
    trim_to_sentence_boundary
)
from src.domain.web_search import (
    WebSearchFetcher,
    fetch_web_context
)


class _KnowModule(sys.modules[__name__].__class__):
    @property
    def DB_FILE(self):
        return _infra_db.DB_FILE

    @DB_FILE.setter
    def DB_FILE(self, value):
        _infra_db.DB_FILE = value

    @property
    def _db_version(self):
        return _infra_db._db_version

    @_db_version.setter
    def _db_version(self, value):
        _infra_db._db_version = value

    @property
    def _cached_doc_vectors(self):
        return _infra_db.MiniVectorEngine._cached_doc_vectors

    @_cached_doc_vectors.setter
    def _cached_doc_vectors(self, value):
        _infra_db.MiniVectorEngine._cached_doc_vectors = value

    @property
    def _cached_inverted_index(self):
        return _infra_db.MiniVectorEngine._cached_inverted_index

    @_cached_inverted_index.setter
    def _cached_inverted_index(self, value):
        _infra_db.MiniVectorEngine._cached_inverted_index = value

sys.modules[__name__].__class__ = _KnowModule

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "init":
        init_db()
    else:
        print("Uroboros Knowledge Engine CLI")

if __name__ == "__main__":
    main()
