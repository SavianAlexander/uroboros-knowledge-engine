"""
Standard Domain & Application Exception Hierarchy.
Provides structured, typed exceptions with HTTP status mappings and error codes.
Standard: Zero-dependency, pure Python standard library.
"""

from typing import Dict, Any, Optional


class UroborosError(Exception):
    """Base domain exception for Uroboros Knowledge Engine."""
    status_code: int = 500
    error_code: str = "INTERNAL_ENGINE_ERROR"

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": "error",
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details
        }


class DocumentNotFoundError(UroborosError):
    """Raised when a requested file, document, or knowledge node does not exist."""
    status_code: int = 404
    error_code: str = "DOCUMENT_NOT_FOUND"


class QueryValidationError(UroborosError):
    """Raised when search, RAG, or query syntax is invalid or malformed."""
    status_code: int = 400
    error_code: str = "INVALID_QUERY_SYNTAX"


class UnauthorizedError(UroborosError):
    """Raised when authentication credentials or API keys are missing or invalid."""
    status_code: int = 401
    error_code: str = "UNAUTHORIZED"


class ForbiddenError(UroborosError):
    """Raised when caller lacks required ACL permissions for a resource."""
    status_code: int = 403
    error_code: str = "FORBIDDEN"


class ResourceConflictError(UroborosError):
    """Raised when creating or renaming a resource that already exists."""
    status_code: int = 409
    error_code: str = "RESOURCE_CONFLICT"


class SearchIndexError(UroborosError):
    """Raised when FTS5 or vector index experiences corruption or search failure."""
    status_code: int = 500
    error_code: str = "SEARCH_INDEX_FAILURE"


class DatabaseLockedError(UroborosError):
    """Raised when SQLite database write timeout occurs under extreme concurrency."""
    status_code: int = 503
    error_code: str = "DATABASE_LOCKED_BUSY"


class RateLimitExceededError(UroborosError):
    """Raised when API client exceeds rate limits."""
    status_code: int = 429
    error_code: str = "RATE_LIMIT_EXCEEDED"
