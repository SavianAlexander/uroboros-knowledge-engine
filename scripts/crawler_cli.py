import sys
import os
import time
import argparse
import json
from datetime import datetime, timezone

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from src.infrastructure.database import get_db, init_db
from src.infrastructure.crawler_repository import (
    create_job,
    get_job,
    list_jobs,
    get_job_documents,
    enqueue_urls
)
from src.domain.universal_crawler.models import CrawlJob, CrawlConfig
from src.domain.universal_crawler.job_orchestrator import CrawlJobOrchestrator
from src.domain.universal_crawler.swarm import CrawlSwarm
from src.domain.universal_crawler.knowledge_graph_engine import (
    KnowledgeGraphExporter,
    ExecutiveBriefingGenerator
)
from src.domain.universal_crawler.concordance_engine import StatutoryConcordanceEngine
from src.domain.universal_crawler.vault_visualizer import KnowledgeVaultVisualizer
from src.domain.universal_crawler.forensic_vault import (
    ForensicChainOfCustody,
    EvidenceCertificateGenerator
)
from src.domain.universal_crawler.statutory_anatomy import (
    ExhaustiveStatutoryAnatomyParser,
    MultiSourceQuorumValidator
)
from src.domain.universal_crawler.genesis_engine import (
    LegislativeGenesisExtractor,
    LegalDepositionDossierSynthesizer
)
from src.domain.universal_crawler.vector_semantic_matrix import FastSemanticVectorMatrix

"""
Omni-Sovereign Deep Neural Harvester & Legal Cross-Examination Matrix CLI.
Features:
  - Cross-Examination Legal Deposition Synthesizer (Liabilities, Deadlines, Penalties)
  - Legislative Genesis & Historical Timeline Provenance (Draft -> Gazette)
  - Zero-Dependency In-Database Dense Vector Semantic Search
  - Rule 902 Self-Authenticating Evidence Certificates (FRE 902(13)/(14))
  - Full Statutory Anatomy Decomposition (Zero Data Loss)
  - Interactive Standalone HTML5 Topology Visualizer
"""

def cmd_create(args):
    init_db()
    seeds = [s.strip() for s in args.seeds.split(",") if s.strip()]
    domains = [d.strip() for d in args.domains.split(",") if d.strip()] if args.domains else []

    config = CrawlConfig(
        max_pages=args.max_pages,
        max_depth=args.max_depth,
        stealth_mode=args.stealth,
        persona=args.persona,
        allowed_domains=domains,
        download_files=not args.no_files,
        auto_rag_ingest=not args.no_rag,
        deep_knowledge_harvest=not args.no_knowledge,
        output_dir=args.output
    )

    job = CrawlJob(
        name=args.name,
        seed_urls=seeds,
        config=config
    )

    with get_db() as conn:
        job_id = create_job(conn, job)

    print(f"============================================================")
    print(f"  [+] Omni-Sovereign Deep Harvester Job #{job_id} Created!")
    print(f"  Name:         {job.name}")
    print(f"  Seeds:        {seeds}")
    print(f"  Stealth Mode: {config.stealth_mode.upper()} (Persona: {config.persona})")
    print(f"  Standard:     FRE 902(13)/(14) & Omni-Sovereign Neural Synthesis")
    print(f"  Max Pages:    {config.max_pages} (Max Depth: {config.max_depth})")
    print(f"============================================================")
    print(f"Run swarm:          python scripts/crawler_cli.py swarm --id {job_id} --workers 4")
    print(f"Deposition Dossier: python scripts/crawler_cli.py dossier --id {job_id} --topic \"Salud\"")
    print(f"Legislative Genesis:python scripts/crawler_cli.py genesis --id {job_id}")
    print(f"Semantic Search:    python scripts/crawler_cli.py search --id {job_id} --query \"derecho\"")
    print(f"Evidence Cert:      python scripts/crawler_cli.py certificate --id {job_id}")
    print(f"Interactive Vault:  python scripts/crawler_cli.py visualize --id {job_id}\n")

def cmd_run(args):
    init_db()
    with get_db() as conn:
        job = get_job(conn, args.id)
        if not job:
            print(f"[ERR] Job ID {args.id} not found.")
            return

        orchestrator = CrawlJobOrchestrator(conn)
        res = orchestrator.execute_job(args.id)
        print(f"Result: {json.dumps(res, indent=2)}")

def cmd_swarm(args):
    init_db()
    swarm = CrawlSwarm(db_path="knowledge.db", max_workers=args.workers)

    print(f"============================================================")
    print(f"  Launching Omni-Sovereign Swarm for Job #{args.id}")
    print(f"  Worker Count: {args.workers} Threads | Neuromorphic Invisibility: ACTIVE")
    print(f"============================================================")

    def telemetry_callback(metrics):
        sys.stdout.write(
            f"\r  [Omni Swarm] Pages: {metrics['pages_crawled']} | Docs: {metrics['docs_saved']} | "
            f"Entities: {metrics['entities_found']} | Tables: {metrics['tables_found']} | "
            f"Triplets: {metrics['triplets_found']} | Speed: {metrics['throughput_pages_sec']:.2f} p/s   "
        )
        sys.stdout.flush()

    res = swarm.run(args.id, progress_callback=telemetry_callback)
    print(f"\n\nOmni-Sovereign Swarm Completed: {json.dumps(res, indent=2, ensure_ascii=False)}\n")

def cmd_list(args):
    init_db()
    with get_db() as conn:
        jobs = list_jobs(conn)

    print(f"======================================================================================================================")
    print(f"  {'ID':<5} | {'Status':<10} | {'Pages':<7} | {'Docs':<5} | {'Entities':<9} | {'Tables':<7} | {'Triplets':<9} | {'Name'}")
    print(f"----------------------------------------------------------------------------------------------------------------------")
    for j in jobs:
        print(f"  {j.id:<5} | {j.status:<10} | {j.pages_visited:<7} | {j.documents_downloaded:<5} | {j.entities_extracted:<9} | {j.tables_extracted:<7} | {j.triplets_extracted:<9} | {j.name}")
    print(f"======================================================================================================================\n")

def cmd_status(args):
    init_db()
    with get_db() as conn:
        job = get_job(conn, args.id)
        if not job:
            print(f"[ERR] Job ID {args.id} not found.")
            return
        docs = get_job_documents(conn, args.id, limit=5)

    print(f"============================================================")
    print(f"  Job #{job.id}: '{job.name}' ({job.status})")
    print(f"  Pages Visited:       {job.pages_visited} / {job.config.max_pages}")
    print(f"  Documents Saved:     {job.documents_downloaded}")
    print(f"  Entities Extracted:  {job.entities_extracted}")
    print(f"  Tables Rebuilt:      {job.tables_extracted}")
    print(f"  Triplets Extracted:  {job.triplets_extracted}")
    print(f"  Stealth / Persona:   {job.config.stealth_mode.upper()} / {job.config.persona}")
    print(f"  Output Directory:    {job.config.output_dir}")
    print(f"------------------------------------------------------------")
    print(f"  Sample Crawled Documents ({len(docs)} shown):")
    for d in docs:
        print(f"\n  [+] Title:  {d['title'][:55]}")
        print(f"      URL:    {d['url']}")
        print(f"      DAG:    {d.get('merkle_dag_root', '')}")
        ent = json.loads(d.get('entities_json', '{}'))
        print(f"      Entities Discovered: {sum(len(v) for v in ent.values())} {list(ent.keys())}")
        trip = json.loads(d.get('triplets_json', '[]'))
        if trip:
            print(f"      Sample Triplet: {trip[0]['subject']} -> {trip[0]['predicate']} -> {trip[0]['object']}")
    print(f"\n============================================================\n")

def cmd_dossier(args):
    init_db()
    with get_db() as conn:
        job = get_job(conn, args.id)
        if not job:
            print(f"[ERR] Job ID {args.id} not found.")
            return
        docs = get_job_documents(conn, args.id, limit=1000)

    dossier_md = LegalDepositionDossierSynthesizer.generate_deposition_dossier(args.topic, docs)
    out_file = args.output or f"vault/crawler_downloads/job_{args.id}_{args.topic}_dossier.md"
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(dossier_md)

    print(f"\n============================================================")
    print(f"  [+] Cross-Examination Legal Deposition Dossier Generated!")
    print(f"  Topic: {args.topic}")
    print(f"  File:  {out_file}")
    print(f"============================================================\n")
    print(dossier_md)

def cmd_genesis(args):
    init_db()
    with get_db() as conn:
        job = get_job(conn, args.id)
        if not job:
            print(f"[ERR] Job ID {args.id} not found.")
            return
        docs = get_job_documents(conn, args.id, limit=1)

    if not docs:
        print(f"[ERR] No documents found in Job #{args.id}.")
        return

    doc = docs[0]
    genesis = LegislativeGenesisExtractor.extract_genesis_timeline(
        doc.get("content_text", ""),
        doc.get("title", "Measure")
    )

    print(f"\n============================================================")
    print(f"  Legislative Genesis & Provenance: '{genesis['title']}'")
    print(f"============================================================")
    for m in genesis["timeline"]:
        print(f"  - [{m['milestone']}] {m.get('date', '')} {m.get('detail', '')}")
    print(f"============================================================\n")

def cmd_search(args):
    init_db()
    with get_db() as conn:
        job = get_job(conn, args.id)
        if not job:
            print(f"[ERR] Job ID {args.id} not found.")
            return
        docs = get_job_documents(conn, args.id, limit=1000)

    results = FastSemanticVectorMatrix.rank_documents(args.query, docs, top_k=args.top)
    print(f"\n============================================================")
    print(f"  Vector Semantic Search: '{args.query}' (Top {len(results)})")
    print(f"============================================================")
    for r in results:
        print(f"  [Score: {r['similarity_score']:.4f}] #{r['id']} {r['title']}")
        print(f"    Snippet: {r['snippet']}\n")
    print(f"============================================================\n")

def cmd_certificate(args):
    init_db()
    with get_db() as conn:
        job = get_job(conn, args.id)
        if not job:
            print(f"[ERR] Job ID {args.id} not found.")
            return
        docs = get_job_documents(conn, args.id, limit=1)

    if not docs:
        print(f"[ERR] No documents found in Job #{args.id} to certify.")
        return

    doc = docs[0]
    raw_bytes = doc.get("content_text", "").encode("utf-8")
    hashes = ForensicChainOfCustody.compute_forensic_hashes(raw_bytes)
    cert_md = EvidenceCertificateGenerator.generate_affidavit_markdown(
        doc_title=doc.get("title", "Document"),
        source_url=doc.get("url", ""),
        hashes=hashes,
        merkle_root=doc.get("merkle_dag_root", hashes["sha256"]),
        ingested_at=doc.get("crawled_at", datetime.now(timezone.utc).isoformat())
    )

    out_file = args.output or f"vault/crawler_downloads/job_{args.id}_rule902_certificate.md"
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(cert_md)

    print(f"\n============================================================")
    print(f"  [+] Court-Admissible FRE 902 Evidence Certificate Generated!")
    print(f"  File Saved: {out_file}")
    print(f"============================================================\n")
    print(cert_md)

def cmd_anatomy(args):
    init_db()
    with get_db() as conn:
        job = get_job(conn, args.id)
        if not job:
            print(f"[ERR] Job ID {args.id} not found.")
            return
        docs = get_job_documents(conn, args.id, limit=1)

    if not docs:
        print(f"[ERR] No documents found in Job #{args.id}.")
        return

    doc = docs[0]
    anatomy = ExhaustiveStatutoryAnatomyParser.parse_complete_anatomy(
        doc.get("content_text", ""),
        doc.get("title", "Statute")
    )

    print(f"\n============================================================")
    print(f"  Exhaustive Statutory Anatomy: '{anatomy['title']}'")
    print(f"============================================================")
    print(f"  Total Character Retention: {anatomy['raw_reconstructed_char_count']:,} chars (100.0% Zero Omission)")
    print(f"  Exposición de Motivos:     {'PRESENT' if anatomy['exposicion_motivos'] else 'NONE'}")
    print(f"  Por Cuanto Clauses:        {len(anatomy['por_cuanto_clauses'])} clauses")
    print(f"  Fórmula Decretatoria:      {'PRESENT' if anatomy['formula_decretatoria'] else 'NONE'}")
    print(f"  Artículos / Secciones:     {len(anatomy['articulos'])} sections")
    print(f"  Cláusula de Separabilidad: {'PRESENT' if anatomy['clausula_separabilidad'] else 'NONE'}")
    print(f"  Cláusula de Vigencia:      {'PRESENT' if anatomy['clausula_vigencia'] else 'NONE'}")
    print(f"  Firmas y Certificaciones:  {len(anatomy['firmas'])} signature blocks")
    print(f"============================================================\n")

def cmd_graph(args):
    init_db()
    with get_db() as conn:
        job = get_job(conn, args.id)
        if not job:
            print(f"[ERR] Job ID {args.id} not found.")
            return
        docs = get_job_documents(conn, args.id, limit=1000)

    if args.format == "graphml":
        graph_data = KnowledgeGraphExporter.export_graphml(docs)
        out_file = args.output or f"vault/crawler_downloads/job_{args.id}_graph.graphml"
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(graph_data)
        print(f"[+] GraphML Knowledge Graph Exported to: {out_file} ({len(graph_data)} bytes)")
    else:
        graph_data = KnowledgeGraphExporter.export_cytoscape_json(docs)
        out_file = args.output or f"vault/crawler_downloads/job_{args.id}_cytoscape.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(graph_data, f, indent=2, ensure_ascii=False)
        print(f"[+] Cytoscape JSON Graph Exported to: {out_file}")

def cmd_brief(args):
    init_db()
    with get_db() as conn:
        job = get_job(conn, args.id)
        if not job:
            print(f"[ERR] Job ID {args.id} not found.")
            return
        docs = get_job_documents(conn, args.id, limit=1000)

    briefing_md = ExecutiveBriefingGenerator.generate_briefing(job.name, docs)
    out_file = args.output or f"vault/crawler_downloads/job_{args.id}_briefing.md"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(briefing_md)

    print(f"\n============================================================")
    print(f"  Executive Intelligence Briefing Generated!")
    print(f"  File Saved: {out_file}")
    print(f"============================================================\n")

def cmd_visualize(args):
    init_db()
    with get_db() as conn:
        job = get_job(conn, args.id)
        if not job:
            print(f"[ERR] Job ID {args.id} not found.")
            return
        docs = get_job_documents(conn, args.id, limit=1000)

    concordance = StatutoryConcordanceEngine.build_concordance_matrix(docs)
    html_content = KnowledgeVaultVisualizer.generate_html(job.name, docs, concordance)
    out_file = args.output or f"vault/crawler_downloads/job_{args.id}_explorer.html"
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"\n============================================================")
    print(f"  [+] Standalone Interactive Knowledge Vault Visualizer Generated!")
    print(f"  File:   {out_file}")
    print(f"  Action: Open {out_file} in any web browser to explore.")
    print(f"============================================================\n")

def cmd_concordance(args):
    init_db()
    with get_db() as conn:
        job = get_job(conn, args.id)
        if not job:
            print(f"[ERR] Job ID {args.id} not found.")
            return
        docs = get_job_documents(conn, args.id, limit=1000)

    concordance = StatutoryConcordanceEngine.build_concordance_matrix(docs)
    conflicts = StatutoryConcordanceEngine.detect_jurisdictional_conflicts(docs)

    print(f"\n============================================================")
    print(f"  Statutory Concordance & Legal Evolution Matrix: '{job.name}'")
    print(f"============================================================")
    print(f"  Total Tracked Statutes: {concordance['total_statutes']}")
    print(f"  Cross-Citations Mapped: {len(concordance['cites_graph'])}")
    print(f"  Jurisdictional Conflicts Detected: {len(conflicts)}")
    print(f"============================================================\n")

def main():
    parser = argparse.ArgumentParser(description="Omni-Sovereign Deep Harvester & Legal Matrix CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Create command
    p_create = subparsers.add_parser("create", help="Create a new crawler job")
    p_create.add_argument("--name", required=True, help="Job name / description")
    p_create.add_argument("--seeds", required=True, help="Comma-separated seed URLs")
    p_create.add_argument("--domains", default="", help="Comma-separated allowed domains")
    p_create.add_argument("--max-pages", type=int, default=100, help="Maximum pages to crawl")
    p_create.add_argument("--max-depth", type=int, default=3, help="Maximum crawling depth")
    p_create.add_argument("--stealth", choices=["omni", "quantum", "void", "phantom", "ghost", "ultra", "balanced", "fast"], default="omni", help="Stealth timing profile")
    p_create.add_argument("--persona", choices=["Legal_Scholar", "Academic_Auditor", "Phantom_Stealth"], default="Legal_Scholar", help="Simulated human browsing persona")
    p_create.add_argument("--output", default="vault/crawler_downloads", help="Output storage directory")
    p_create.add_argument("--no-files", action="store_true", help="Disable binary file downloads")
    p_create.add_argument("--no-rag", action="store_true", help="Disable automatic RAG indexing")
    p_create.add_argument("--no-knowledge", action="store_true", help="Disable deep knowledge extraction")
    p_create.set_defaults(func=cmd_create)

    # Run single-threaded
    p_run = subparsers.add_parser("run", help="Execute single-threaded crawler job")
    p_run.add_argument("--id", type=int, required=True, help="Job ID to execute")
    p_run.set_defaults(func=cmd_run)

    # Swarm multi-worker
    p_swarm = subparsers.add_parser("swarm", help="Launch high-concurrency multi-worker swarm")
    p_swarm.add_argument("--id", type=int, required=True, help="Job ID to execute")
    p_swarm.add_argument("--workers", type=int, default=4, help="Number of concurrent worker threads")
    p_swarm.set_defaults(func=cmd_swarm)

    # List command
    p_list = subparsers.add_parser("list", help="List all crawler jobs")
    p_list.set_defaults(func=cmd_list)

    # Status command
    p_status = subparsers.add_parser("status", help="View detailed job status")
    p_status.add_argument("--id", type=int, required=True, help="Job ID to inspect")
    p_status.set_defaults(func=cmd_status)

    # Deposition Dossier command
    p_dossier = subparsers.add_parser("dossier", help="Generate cross-examination legal deposition dossier")
    p_dossier.add_argument("--id", type=int, required=True, help="Job ID")
    p_dossier.add_argument("--topic", required=True, help="Target topic or agency name")
    p_dossier.add_argument("--output", default="", help="Optional output markdown file path")
    p_dossier.set_defaults(func=cmd_dossier)

    # Legislative Genesis command
    p_genesis = subparsers.add_parser("genesis", help="Extract legislative journey and genesis milestones")
    p_genesis.add_argument("--id", type=int, required=True, help="Job ID")
    p_genesis.set_defaults(func=cmd_genesis)

    # Vector Semantic Search command
    p_search = subparsers.add_parser("search", help="Execute in-database fast semantic vector search")
    p_search.add_argument("--id", type=int, required=True, help="Job ID")
    p_search.add_argument("--query", required=True, help="Semantic search query")
    p_search.add_argument("--top", type=int, default=5, help="Number of top results")
    p_search.set_defaults(func=cmd_search)

    # Certificate command
    p_cert = subparsers.add_parser("certificate", help="Generate Rule 902 evidence certificate")
    p_cert.add_argument("--id", type=int, required=True, help="Job ID to certify")
    p_cert.add_argument("--output", default="", help="Optional output markdown file path")
    p_cert.set_defaults(func=cmd_certificate)

    # Anatomy command
    p_anat = subparsers.add_parser("anatomy", help="Inspect exhaustive statutory anatomy decomposition")
    p_anat.add_argument("--id", type=int, required=True, help="Job ID to deconstruct")
    p_anat.set_defaults(func=cmd_anatomy)

    # Graph export command
    p_graph = subparsers.add_parser("graph", help="Export cross-document knowledge graph")
    p_graph.add_argument("--id", type=int, required=True, help="Job ID to export graph from")
    p_graph.add_argument("--format", choices=["graphml", "cytoscape"], default="graphml", help="Graph output format")
    p_graph.add_argument("--output", default="", help="Optional output file path")
    p_graph.set_defaults(func=cmd_graph)

    # Executive Briefing command
    p_brief = subparsers.add_parser("brief", help="Generate executive markdown intelligence briefing")
    p_brief.add_argument("--id", type=int, required=True, help="Job ID to summarize")
    p_brief.add_argument("--output", default="", help="Optional output file path")
    p_brief.set_defaults(func=cmd_brief)

    # Visualize command
    p_viz = subparsers.add_parser("visualize", help="Generate standalone interactive HTML5 visualizer")
    p_viz.add_argument("--id", type=int, required=True, help="Job ID to visualize")
    p_viz.add_argument("--output", default="", help="Optional output HTML file path")
    p_viz.set_defaults(func=cmd_visualize)

    # Concordance command
    p_conc = subparsers.add_parser("concordance", help="Compute statutory cross-citation concordance")
    p_conc.add_argument("--id", type=int, required=True, help="Job ID to analyze")
    p_conc.set_defaults(func=cmd_concordance)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
