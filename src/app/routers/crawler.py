import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from fastapi.responses import HTMLResponse, PlainTextResponse, JSONResponse
from pydantic import BaseModel, Field

from src.infrastructure.database import get_db
from src.infrastructure.crawler_repository import (
    create_job,
    get_job,
    list_jobs,
    get_job_documents,
    update_job_status
)
from src.domain.universal_crawler.models import CrawlJob, CrawlConfig
from src.domain.universal_crawler.swarm import CrawlSwarm
from src.domain.universal_crawler.forensic_vault import (
    ForensicChainOfCustody,
    EvidenceCertificateGenerator
)
from src.domain.universal_crawler.genesis_engine import (
    LegislativeGenesisExtractor,
    LegalDepositionDossierSynthesizer
)
from src.domain.universal_crawler.vault_visualizer import KnowledgeVaultVisualizer
from src.domain.universal_crawler.concordance_engine import StatutoryConcordanceEngine
from src.domain.universal_crawler.vector_semantic_matrix import FastSemanticVectorMatrix

router = APIRouter(prefix="/api/crawler", tags=["Universal Crawler & Knowledge Matrix"])

# Global swarm runner registry
_active_swarms: Dict[int, CrawlSwarm] = {}

class CreateJobRequest(BaseModel):
    name: str = Field(..., description="Job name")
    seed_urls: List[str] = Field(..., description="Initial seed URLs")
    allowed_domains: Optional[List[str]] = Field(default_factory=list, description="Allowed domains filter")
    max_pages: Optional[int] = Field(default=100, description="Max pages limit")
    max_depth: Optional[int] = Field(default=3, description="Max crawl depth")
    stealth_mode: Optional[str] = Field(default="omni", description="Stealth timing tier")
    persona: Optional[str] = Field(default="Legal_Scholar", description="Simulated persona")
    download_files: Optional[bool] = Field(default=True, description="Download binary files (PDFs)")
    auto_rag_ingest: Optional[bool] = Field(default=True, description="Auto RAG vectorization")

class SemanticSearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    top_k: Optional[int] = Field(default=5, description="Number of results")

@router.get("/jobs")
def api_list_jobs():
    """List all crawler jobs with status and extracted metrics."""
    with get_db() as conn:
        jobs = list_jobs(conn)
    return {
        "status": "success",
        "total_jobs": len(jobs),
        "jobs": [
            {
                "id": j.id,
                "name": j.name,
                "status": j.status,
                "pages_visited": j.pages_visited,
                "documents_downloaded": j.documents_downloaded,
                "entities_extracted": j.entities_extracted,
                "tables_extracted": j.tables_extracted,
                "triplets_extracted": j.triplets_extracted,
                "stealth_mode": j.config.stealth_mode,
                "created_at": j.created_at
            }
            for j in jobs
        ]
    }

@router.post("/jobs")
def api_create_job(req: CreateJobRequest):
    """Create a new crawl job defaulting to stealth mode."""
    config = CrawlConfig(
        max_pages=req.max_pages or 100,
        max_depth=req.max_depth or 3,
        stealth_mode=req.stealth_mode or "omni",
        persona=req.persona or "Legal_Scholar",
        allowed_domains=req.allowed_domains or [],
        download_files=req.download_files if req.download_files is not None else True,
        auto_rag_ingest=req.auto_rag_ingest if req.auto_rag_ingest is not None else True,
        deep_knowledge_harvest=True
    )
    job = CrawlJob(
        name=req.name,
        seed_urls=req.seed_urls,
        config=config
    )
    with get_db() as conn:
        job_id = create_job(conn, job)

    return {
        "status": "success",
        "job_id": job_id,
        "name": job.name,
        "stealth_mode": config.stealth_mode,
        "message": f"Crawler Job #{job_id} created successfully."
    }

@router.get("/jobs/{job_id}")
def api_get_job(job_id: int):
    """Get detailed telemetry, status, and sample documents for a job."""
    with get_db() as conn:
        job = get_job(conn, job_id)
        if not job:
            raise HTTPException(status_code=404, detail=f"Job #{job_id} not found")
        docs = get_job_documents(conn, job_id, limit=10)

    return {
        "status": "success",
        "job": {
            "id": job.id,
            "name": job.name,
            "status": job.status,
            "pages_visited": job.pages_visited,
            "documents_downloaded": job.documents_downloaded,
            "entities_extracted": job.entities_extracted,
            "tables_extracted": job.tables_extracted,
            "triplets_extracted": job.triplets_extracted,
            "config": json.loads(job.config.to_json()),
            "created_at": job.created_at
        },
        "sample_documents": [
            {
                "id": d["id"],
                "title": d["title"],
                "url": d["url"],
                "merkle_dag_root": d.get("merkle_dag_root"),
                "crawled_at": d["crawled_at"]
            }
            for d in docs
        ]
    }

@router.post("/jobs/{job_id}/start")
def api_start_job(job_id: int, background_tasks: BackgroundTasks, workers: int = Query(default=4, ge=1, le=16)):
    """Launch high-concurrency crawler worker swarm in background."""
    with get_db() as conn:
        job = get_job(conn, job_id)
        if not job:
            raise HTTPException(status_code=404, detail=f"Job #{job_id} not found")

    if job_id in _active_swarms:
        return {"status": "running", "message": f"Swarm for Job #{job_id} is already active."}

    swarm = CrawlSwarm(db_path="knowledge.db", max_workers=workers)
    _active_swarms[job_id] = swarm

    def run_swarm():
        try:
            swarm.run(job_id)
        finally:
            _active_swarms.pop(job_id, None)

    background_tasks.add_task(run_swarm)
    return {
        "status": "started",
        "job_id": job_id,
        "workers": workers,
        "message": f"Crawler Swarm with {workers} workers started in background."
    }

@router.post("/jobs/{job_id}/stop")
def api_stop_job(job_id: int):
    """Gracefully signal active crawler swarm to stop."""
    swarm = _active_swarms.get(job_id)
    if not swarm:
        with get_db() as conn:
            update_job_status(conn, job_id, "PAUSED")
        return {"status": "stopped", "message": f"Job #{job_id} marked as PAUSED."}

    swarm.request_stop()
    return {"status": "stopping", "message": f"Stop signal dispatched to Job #{job_id} swarm."}

@router.get("/jobs/{job_id}/certificate")
def api_get_certificate(job_id: int):
    """Generate and return Rule 902 Self-Authenticating Evidence Certificate."""
    with get_db() as conn:
        job = get_job(conn, job_id)
        if not job:
            raise HTTPException(status_code=404, detail=f"Job #{job_id} not found")
        docs = get_job_documents(conn, job_id, limit=1)

    if not docs:
        raise HTTPException(status_code=404, detail=f"No documents found in Job #{job_id} to certify.")

    doc = docs[0]
    raw_bytes = doc.get("content_text", "").encode("utf-8")
    hashes = ForensicChainOfCustody.compute_forensic_hashes(raw_bytes)
    cert_md = EvidenceCertificateGenerator.generate_affidavit_markdown(
        doc_title=doc.get("title", "Document"),
        source_url=doc.get("url", ""),
        hashes=hashes,
        merkle_root=doc.get("merkle_dag_root", hashes["sha256"]),
        ingested_at=doc.get("crawled_at", "")
    )
    cert_json_ld = EvidenceCertificateGenerator.generate_affidavit_json_ld(
        doc_title=doc.get("title", "Document"),
        source_url=doc.get("url", ""),
        hashes=hashes,
        merkle_root=doc.get("merkle_dag_root", hashes["sha256"]),
        ingested_at=doc.get("crawled_at", "")
    )

    return {
        "status": "success",
        "job_id": job_id,
        "doc_id": doc["id"],
        "title": doc["title"],
        "markdown_certificate": cert_md,
        "json_ld_manifest": cert_json_ld
    }

@router.get("/jobs/{job_id}/dossier")
def api_get_dossier(job_id: int, topic: str = Query(..., description="Target topic or agency name")):
    """Generate and return Legal Deposition Cross-Examination Dossier."""
    with get_db() as conn:
        job = get_job(conn, job_id)
        if not job:
            raise HTTPException(status_code=404, detail=f"Job #{job_id} not found")
        docs = get_job_documents(conn, job_id, limit=1000)

    dossier_md = LegalDepositionDossierSynthesizer.generate_deposition_dossier(topic, docs)
    return {
        "status": "success",
        "job_id": job_id,
        "topic": topic,
        "dossier_markdown": dossier_md
    }

@router.get("/jobs/{job_id}/genesis")
def api_get_genesis(job_id: int):
    """Extract legislative genesis timeline for documents in job."""
    with get_db() as conn:
        job = get_job(conn, job_id)
        if not job:
            raise HTTPException(status_code=404, detail=f"Job #{job_id} not found")
        docs = get_job_documents(conn, job_id, limit=5)

    timelines = []
    for d in docs:
        gen = LegislativeGenesisExtractor.extract_genesis_timeline(
            d.get("content_text", ""),
            d.get("title", "Measure")
        )
        timelines.append(gen)

    return {
        "status": "success",
        "job_id": job_id,
        "timelines": timelines
    }

@router.get("/jobs/{job_id}/visualizer", response_class=HTMLResponse)
def api_get_visualizer(job_id: int):
    """Generate and serve the standalone interactive HTML5 Knowledge Vault visualizer."""
    with get_db() as conn:
        job = get_job(conn, job_id)
        if not job:
            raise HTTPException(status_code=404, detail=f"Job #{job_id} not found")
        docs = get_job_documents(conn, job_id, limit=1000)

    concordance = StatutoryConcordanceEngine.build_concordance_matrix(docs)
    html_content = KnowledgeVaultVisualizer.generate_html(job.name, docs, concordance)
    return HTMLResponse(content=html_content, status_code=200)

@router.post("/jobs/{job_id}/search")
def api_search_job(job_id: int, req: SemanticSearchRequest):
    """Execute in-database fast dense semantic vector search."""
    with get_db() as conn:
        job = get_job(conn, job_id)
        if not job:
            raise HTTPException(status_code=404, detail=f"Job #{job_id} not found")
        docs = get_job_documents(conn, job_id, limit=1000)

    results = FastSemanticVectorMatrix.rank_documents(req.query, docs, top_k=req.top_k or 5)
    return {
        "status": "success",
        "job_id": job_id,
        "query": req.query,
        "results": results
    }
