"""
Tabular dataset operations router.
Includes dynamic dataset ingestion & orchestration, Text-to-SQL querying,
database self-healing, relational foreign-key linking, multi-table joins,
automated data cleaning, and statistical exploratory data profiling.
"""
import logging
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Body

logger = logging.getLogger(__name__)

router = APIRouter()

# ---------------------------------------------------------------------------
# Declarative Pipeline Schemas
# ---------------------------------------------------------------------------

class DataOrchestrateRequest(BaseModel):
    dataset_name: str = Field("client_dataset", description="Name of the target dataset table to provision")
    raw_content: str = Field(..., description="Raw tabular string, CSV, TSV, JSON, or XML content")
    format_hint: Optional[str] = Field(None, description="Optional format hint (e.g. csv, json, xml, tsv)")


class DataQueryRequest(BaseModel):
    query: str = Field(..., description="Natural language question to translate and execute via Text-to-SQL")


class DataJoinRequest(BaseModel):
    query: str = Field(..., description="Natural language query requesting multi-table correlation")
    dataset_names: Optional[List[str]] = Field(None, description="Explicit dataset table names to join")


class DataCleanRequest(BaseModel):
    dataset_name: str = Field(..., description="Target dataset table name to cleanse and normalize")


class DataProfileRequest(BaseModel):
    dataset_name: str = Field(..., description="Target dataset table name to compute statistical profiles for")


# ---------------------------------------------------------------------------
# Tabular Dataset Endpoints
# ---------------------------------------------------------------------------

@router.post("/api/data/orchestrate")
def orchestrate_data_endpoint(payload: Union[DataOrchestrateRequest, Dict[str, Any]] = Body(...)):
    """Autonomously ingests polymorphic client data, infers schema, and provisions dynamic SQLite tables."""
    if isinstance(payload, DataOrchestrateRequest):
        name = payload.dataset_name or "client_dataset"
        content = payload.raw_content
        format_hint = payload.format_hint
    else:
        name = payload.get("dataset_name", "client_dataset")
        content = payload.get("raw_content", "")
        format_hint = payload.get("format_hint")

    if not content:
        raise HTTPException(status_code=400, detail="raw_content is required")
    try:
        from src.domain.polymorphic_data_orchestrator import provision_dynamic_dataset
        return provision_dynamic_dataset(name, content, format_hint)
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        logger.exception("Failed to orchestrate client dataset %s: %s", name, e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/data/datasets")
def list_datasets_endpoint():
    """Lists all dynamically orchestrated client datasets with discovered schemas."""
    try:
        from src.domain.polymorphic_data_orchestrator import list_orchestrated_datasets
        return {"datasets": list_orchestrated_datasets()}
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        logger.exception("Failed to list orchestrated datasets: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/data/query")
def query_data_endpoint(payload: Union[DataQueryRequest, Dict[str, Any]] = Body(...)):
    """Autonomously routes natural language questions to dynamic client tables via Text-to-SQL."""
    if isinstance(payload, DataQueryRequest):
        query = payload.query
    else:
        query = payload.get("query", "")

    if not query:
        raise HTTPException(status_code=400, detail="query is required")
    try:
        from src.domain.autonomous_sql_router import execute_autonomous_sql_query
        return execute_autonomous_sql_query(query)
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        logger.exception("Failed to execute autonomous SQL query: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/data/health")
def database_health_endpoint():
    """Runs autonomous database index optimization, anomaly detection, and WAL self-healing."""
    try:
        from src.domain.knowledge_self_healing import execute_database_self_healing
        return execute_database_self_healing()
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        logger.exception("Failed to check database health: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/data/relationships")
def data_relationships_endpoint():
    """Discovers foreign keys and relational linkages across dynamically provisioned client datasets."""
    try:
        from src.domain.relational_schema_linker import discover_foreign_key_relationships, generate_mermaid_er_diagram
        return {
            "relationships": discover_foreign_key_relationships(),
            "er_diagram": generate_mermaid_er_diagram()
        }
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        logger.exception("Failed to discover data relationships: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/data/join")
def data_join_endpoint(payload: Union[DataJoinRequest, Dict[str, Any]] = Body(...)):
    """Synthesizes and executes multi-table SQL JOIN queries across related client datasets."""
    if isinstance(payload, DataJoinRequest):
        query = payload.query
        dataset_names = payload.dataset_names
    else:
        query = payload.get("query", "")
        dataset_names = payload.get("dataset_names")

    try:
        from src.domain.relational_schema_linker import synthesize_multi_table_join
        return synthesize_multi_table_join(query, dataset_names)
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        logger.exception("Failed to synthesize data join: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/data/clean")
def data_clean_endpoint(payload: Union[DataCleanRequest, Dict[str, Any]] = Body(...)):
    """Executes automated missing value imputation, date normalization, and deduplication on a client dataset."""
    if isinstance(payload, DataCleanRequest):
        dataset_name = payload.dataset_name
    else:
        dataset_name = payload.get("dataset_name", "")

    if not dataset_name:
        raise HTTPException(status_code=400, detail="dataset_name is required")
    try:
        from src.domain.client_data_cleaner import cleanse_client_dataset
        return cleanse_client_dataset(dataset_name)
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        logger.exception("Failed to cleanse client dataset %s: %s", dataset_name, e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/data/profile")
def data_profile_endpoint(payload: Union[DataProfileRequest, Dict[str, Any]] = Body(...)):
    """Computes automated exploratory data analysis, Pearson correlations, and statistical summaries."""
    if isinstance(payload, DataProfileRequest):
        dataset_name = payload.dataset_name
    else:
        dataset_name = payload.get("dataset_name", "")

    if not dataset_name:
        raise HTTPException(status_code=400, detail="dataset_name is required")
    try:
        from src.domain.statistical_data_profiler import profile_client_dataset
        return profile_client_dataset(dataset_name)
    except (KeyboardInterrupt, MemoryError, SystemExit):
        raise
    except Exception as e:
        logger.exception("Failed to profile client dataset %s: %s", dataset_name, e)
        raise HTTPException(status_code=500, detail=str(e))
