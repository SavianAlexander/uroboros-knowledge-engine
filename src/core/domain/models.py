"""
Domain models and request/response schemas supporting dual field naming (filepath / path, query / message, prompt / text).
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class RAGStreamRequest(BaseModel):
    query: Optional[str] = None
    message: Optional[str] = None
    max_chunks: Optional[int] = 5

    def get_query(self) -> str:
        return self.query or self.message or ""

class RevertRequest(BaseModel):
    filepath: Optional[str] = None
    path: Optional[str] = None
    revision_id: int

    def get_path(self) -> str:
        return self.filepath or self.path or ""

class DeleteFileRequest(BaseModel):
    filepath: Optional[str] = None
    path: Optional[str] = None

    def get_path(self) -> str:
        return self.filepath or self.path or ""

class BookmarkRequest(BaseModel):
    name: Optional[str] = None
    query: Optional[str] = None
    query_string: Optional[str] = None
    search_mode: Optional[str] = "keyword"

    def get_query(self) -> str:
        return self.query or self.query_string or ""

class DeleteBookmarkRequest(BaseModel):
    name: str

class IndexRequest(BaseModel):
    dir_path: Optional[str] = None
    directory: Optional[str] = None

    def get_dir(self) -> str:
        return self.dir_path or self.directory or ""

class TagRequest(BaseModel):
    filepath: Optional[str] = None
    path: Optional[str] = None
    tag: str

    def get_path(self) -> str:
        return self.filepath or self.path or ""

class NotesRequest(BaseModel):
    filepath: Optional[str] = None
    path: Optional[str] = None
    notes: str

    def get_path(self) -> str:
        return self.filepath or self.path or ""

class RenameRequest(BaseModel):
    filepath: Optional[str] = None
    path: Optional[str] = None
    new_name: str
    overwrite: Optional[bool] = False

    def get_path(self) -> str:
        return self.filepath or self.path or ""

class FileSaveRequest(BaseModel):
    filepath: Optional[str] = None
    path: Optional[str] = None
    content: str

    def get_path(self) -> str:
        return self.filepath or self.path or ""

class FileEditRequest(BaseModel):
    filepath: Optional[str] = None
    path: Optional[str] = None
    content: str

    def get_path(self) -> str:
        return self.filepath or self.path or ""

class RuleRequest(BaseModel):
    pattern: str
    tag: str
    priority: Optional[int] = 0

class TagColorRequest(BaseModel):
    tag: str
    color: str

class BulkDeleteRequest(BaseModel):
    filepaths: List[str]

class MacroRequest(BaseModel):
    name: str
    expansion: str

class AliasRequest(BaseModel):
    tag: Optional[str] = None
    canonical_tag: Optional[str] = None
    alias: Optional[str] = None
    target: Optional[str] = None

    def get_alias(self) -> str:
        return self.alias or self.tag or ""

    def get_target(self) -> str:
        return self.target or self.canonical_tag or ""

class ValidateQueryRequest(BaseModel):
    query: str

class SynonymRequest(BaseModel):
    term: str
    synonyms: Optional[List[str]] = None
    synonym: Optional[str] = None

class BackupScheduleRequest(BaseModel):
    interval_minutes: int

class PeerRequest(BaseModel):
    address: str
    name: Optional[str] = ""

class SyncExchangeRequest(BaseModel):
    peer: Optional[str] = None
    target_peer: Optional[str] = None
    manifest: Optional[Dict[str, Any]] = None

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: Optional[List[ChatMessage]] = None
    message: Optional[str] = None
    history: Optional[List[ChatMessage]] = None
    model: Optional[str] = None
    temperature: Optional[float] = 0.3
    top_p: Optional[float] = 0.9
    session_id: Optional[str] = None
    web_search: Optional[bool] = False
    enable_web_search: Optional[bool] = False


class ChatResponse(BaseModel):
    response: str
    sources: Optional[List[dict]] = []

class FileInsightsRequest(BaseModel):
    filepath: Optional[str] = None
    path: Optional[str] = None
    temperature: Optional[float] = 0.3
    top_p: Optional[float] = 0.9

    def get_path(self) -> str:
        return self.filepath or self.path or ""

class FileInsightsResponse(BaseModel):
    insights: str

class OpenFileRequest(BaseModel):
    filepath: Optional[str] = None
    path: Optional[str] = None

    def get_path(self) -> str:
        return self.filepath or self.path or ""

class ContemplateRequest(BaseModel):
    prompt: Optional[str] = None
    text: Optional[str] = None
    mode: Optional[str] = "standard"

    def get_prompt(self) -> str:
        return self.prompt or self.text or ""

class ContemplateResponse(BaseModel):
    core_problem: str
    risk_profile: str
    friction_cost: str
    velocity: str
    raw_analysis: str

from pydantic import BaseModel, Field, ConfigDict

class CreateSessionRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    title: Optional[str] = None
    model_path: Optional[str] = None
    temperature: Optional[float] = 0.7
    context_window: Optional[int] = 4096
    metadata_json: Optional[Any] = None

class UpdateSessionRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    title: Optional[str] = None
    model_path: Optional[str] = None
    temperature: Optional[float] = None
    context_window: Optional[int] = None
    metadata_json: Optional[Any] = None

class AddMessageRequest(BaseModel):
    role: str = "user"
    content: str
    citations_json: Optional[Any] = None
    web_sources_json: Optional[Any] = None
    tokens_used: Optional[int] = 0
    metadata_json: Optional[Any] = None


class AnalyticsOverviewResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    total_documents: int = 0
    total_chunks: int = 0
    fts_records: int = 0
    indexing_status: str = "idle"
    storage_total_bytes: int = 0


class StorageBreakdownResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    by_mime: Dict[str, int] = Field(default_factory=dict)
    by_extension: Dict[str, int] = Field(default_factory=dict)
    top_directories: List[Dict[str, Any]] = Field(default_factory=list)


class TagDistributionResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    total_tags: int = 0
    top_tags: List[Dict[str, Any]] = Field(default_factory=list)
    tag_cooccurrence: List[Dict[str, Any]] = Field(default_factory=list)


class SearchActivityResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    total_queries: int = 0
    avg_latency_ms: float = 0.0
    top_queries: List[Dict[str, Any]] = Field(default_factory=list)
    recent_queries: List[Dict[str, Any]] = Field(default_factory=list)


class WorkflowTriggerCreate(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    name: str
    event_type: str
    condition_pattern: Optional[str] = ""
    webhook_url: str
    secret_header: Optional[str] = ""
    is_active: Optional[bool] = True


class WorkflowTriggerUpdate(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    name: Optional[str] = None
    event_type: Optional[str] = None
    condition_pattern: Optional[str] = None
    webhook_url: Optional[str] = None
    secret_header: Optional[str] = None
    is_active: Optional[bool] = None


class WorkflowTriggerResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    id: int
    name: str
    event_type: str
    condition_pattern: Optional[str] = ""
    webhook_url: str
    secret_header: Optional[str] = ""
    is_active: int
    created_at: str
    updated_at: str


class WorkflowLogResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    id: int
    trigger_id: Optional[int] = None
    event_type: str
    payload_json: str
    status: str
    response_status_code: Optional[int] = None
    response_body: Optional[str] = ""
    execution_time_ms: float = 0.0
    retry_count: int = 0
    executed_at: str


class WorkflowEventTriggerRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    event_type: Optional[str] = None
    trigger_id: Optional[int] = None
    payload: Optional[Dict[str, Any]] = Field(default_factory=dict)




