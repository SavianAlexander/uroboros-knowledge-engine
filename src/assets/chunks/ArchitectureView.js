import{r as o,j as e}from"./vendor-react.js";import{b as S}from"../app.js";import{ar as C,a6 as f,ad as v,i as p,g as u,av as R,e as g,C as N,u as A,v as k,m as T,Z as w}from"./vendor-icons.js";import"./vendor-motion.js";import"./vendor-charts.js";import"./vendor-3d-graph.js";const i=[{id:"tri-engine",title:"Tri-Engine Orchestration",subtitle:"Neuro Vector Vault + Tududi Task Master + GitHub Merkle Engine",category:"TRI_ENGINE",icon:C,badge:"TRI-ENGINE",badgeColor:"emerald",description:"Synchronized tripartite execution loop binding local semantic intelligence, autonomous project task orchestration, and cryptographic git commit provenance.",keyMetrics:[{label:"Throughput",value:"43 Ops/Sec"},{label:"Provenance",value:"SHA-256 Merkle"},{label:"Task Sync",value:"Tududi #13"},{label:"Isolation",value:"Air-Gapped"}],mermaidCode:`graph TB
    subgraph Engine1["1. Neuro Knowledge Engine"]
        FTS5[("SQLite FTS5 Lexical Vault")]
        ColBERT["Binary ColBERT Vector Engine"]
        GraphDB["SQLite HyperGraph Engine"]
        Ollama["Local Ollama Neural Router"]
    end

    subgraph Engine2["2. Tududi Task Master"]
        TaskDB[("PostgreSQL / SQLite Task Store")]
        SprintEngine["Project #13 Sprint Tracker"]
        Habits["Habit & Goal Synchronizer"]
        AuditTrail["Autonomous Execution Audit Trail"]
    end

    subgraph Engine3["3. GitHub & Merkle Provenance"]
        GitCLI["GitHub CLI Bridge"]
        MerkleEngine["SHA-256 Merkle Provenance Engine"]
        CIWorkflows["GitHub Actions Automated Matrix"]
        ReleaseCert["SOC 2 Provenance Attestation"]
    end

    Agent["Antigravity AI Agent / Senior Dev"] -->|FastAPI REST & MCP| Engine1
    Agent -->|Tududi MCP & REST| Engine2
    Agent -->|Git / GitHub Bridge CLI| Engine3

    Engine1 <-->|Context-Informed Flight Plans| Engine2
    Engine2 <-->|Automated Issue & Task Sync| Engine3
    Engine3 <-->|SOC 2 Cryptographic Root Signatures| Engine1`,steps:[{title:"Knowledge Triangulation",desc:"Queries SQLite FTS5 and ColBERT vector embeddings for local context.",latency:"12ms"},{title:"Autonomous Task Logging",desc:"Dispatches enriched flight plan into Tududi Project #13 Task Master.",latency:"8ms"},{title:"Merkle Provenance Attestation",desc:"Computes cryptographic SHA-256 state hash and signs release certificate.",latency:"15ms"}]},{id:"10-bridge-dag",title:"10-Bridge Asynchronous Parallel DAG",subtitle:"Concurrent Multi-Bridge Contract Execution Protocol",category:"PIPELINE",icon:f,badge:"ASYNC-DAG",badgeColor:"blue",description:"3-stage asynchronous directed acyclic graph executing independent discovery, contextual verification, and cryptographic contract compilation concurrently.",keyMetrics:[{label:"Parallel Bridges",value:"10 Engines"},{label:"Contract Fidelity",value:"100%"},{label:"Total Stage Time",value:"~19.9s"},{label:"Zero-Reboot Recovery",value:"Active"}],mermaidCode:`graph TD
    subgraph Stage1["Stage 1: Concurrent Independent Discovery (Parallel Gather)"]
        B1["Architecture Bridge<br/>(AST & Clean Arch Doctor)"]
        B2["Tududi Bridge<br/>(Task Master Burndown)"]
        B3["GitHub Bridge<br/>(Git & Merkle Hash)"]
        B4["Visual Audit Bridge<br/>(Layout QA & CSS Sync)"]
        B5["Process Hygiene Bridge<br/>(OS Memory & Process Audit)"]
    end

    subgraph Stage2["Stage 2: Context-Informed Verification (Parallel Async)"]
        B6["Snapshot Bridge<br/>(Client Showcase & Deck Generator)"]
        B7["Neuro Bridge<br/>(ColBERT Vector Vault Verification)"]
        B8["EVE Online Fleet Bridge<br/>(ESI Telemetry & Physics Model)"]
        B9["System Recovery Bridge<br/>(Zero-Reboot Windows Recovery)"]
    end

    subgraph Stage3["Stage 3: Verification & Provenance Ledger"]
        Ledger[("Persistent Execution Ledger")]
        Cert["SOC 2 Type II Merkle Certificate"]
    end

    Trigger["Co-Pilot Execution Trigger"] --> Stage1
    B1 & B2 & B3 & B4 & B5 --> Stage2
    B6 & B7 & B8 & B9 --> Stage3
    Stage3 --> Ledger
    Stage3 --> Cert`,steps:[{title:"Stage 1: Independent Discovery",desc:"Concurrently runs Architecture, Tududi, GitHub, Visual Audit, and Process Hygiene.",latency:"2.3s"},{title:"Stage 2: Contextual Verification",desc:"Executes Snapshot, ColBERT Vector Vault, EVE Telemetry, and System Recovery.",latency:"2.4s"},{title:"Stage 3: Contract Compilation",desc:"Compiles immutable execution ledger and issues SHA-256 certificate.",latency:"0.7s"}]},{id:"universal-crawler",title:"Universal Crawler & Legal Intelligence Subsystem",subtitle:"Adaptive Multi-Session Harvesting & Statutory Anatomy Parser",category:"PIPELINE",icon:v,badge:"CRAWLER-LEGAL",badgeColor:"amber",description:"High-performance web crawler supporting 6 session engines, PDF OCR text extraction, and automatic concordance mapping for statutory legal codes.",keyMetrics:[{label:"Session Engines",value:"6 Modes"},{label:"Domain Rate Limiter",value:"Adaptive"},{label:"Legal Codes",value:"PR 1952/2012/2020"},{label:"Forensic Vault",value:"SQLite Indexed"}],mermaidCode:`flowchart LR
    subgraph Input["Job Configuration"]
        TargetURL["Target URL / Legal Portal"]
        SessionMode{"Session Mode"}
    end

    subgraph CrawlerEngine["Crawler Orchestration Engine"]
        Frontier["Priority Frontier Queue"]
        RateLimiter["Adaptive Domain Rate Limiter"]
        
        subgraph SessionEngines["Session Harvesting Engines"]
            S1["Adaptive Session"]
            S2["Browser Automation"]
            S3["Proxy Rotation"]
            S4["Async Worker Pool"]
            S5["Rotating Headers"]
            S6["Direct Session"]
        end

        Extractor["Deep Content Extractor"]
        Forensic["Forensic Ingestion Vault"]
    end

    subgraph LegalDomain["Puerto Rico Legal & Knowledge Core"]
        Statutory["Statutory Anatomy Parser"]
        Constitucion["Constitucion ELA 1952"]
        CodCivil["Codigo Civil 2020"]
        CodPenal["Codigo Penal 2012"]
        PDFExtract["OCR & PDF Text Extraction"]
    end

    TargetURL --> Frontier
    SessionMode --> Frontier
    Frontier --> RateLimiter
    RateLimiter --> S1 & S2 & S3 & S4 & S5 & S6
    S1 & S2 & S3 & S4 & S5 & S6 --> Extractor
    Extractor --> Forensic
    Forensic --> Statutory
    Statutory --> Constitucion & CodCivil & CodPenal & PDFExtract`,steps:[{title:"Frontier Queuing",desc:"Dispatches target URLs to adaptive session pools with politeness throttling.",latency:"15ms"},{title:"Statutory Parsing",desc:"Extracts articles, sections, and cross-references from legal codes.",latency:"45ms"},{title:"Vector Concordance",desc:"Generates dense vector embeddings and links into SQLite HyperGraph.",latency:"80ms"}]},{id:"hybrid-retrieval",title:"5-Pass Hybrid Retrieval Pipeline",subtitle:"Okapi BM25 + ColBERT Vector + Graph Traversal + MaxSim Rerank",category:"INFRASTRUCTURE",icon:p,badge:"5-PASS RAG",badgeColor:"purple",description:"Multi-pass retrieval pipeline combining sub-50ms HyDE expansion, SQLite FTS5 lexical matching, binary ColBERT MaxSim reranking, and multi-agent debate validation.",keyMetrics:[{label:"HyDE Expansion",value:"< 50ms"},{label:"RRF Constant",value:"k = 60"},{label:"Confidence Guard",value:">= 0.65"},{label:"Passage Dedupe",value:"MinHash Jaccard"}],mermaidCode:`sequenceDiagram
    autonumber
    actor User as User / API Client
    participant Router as Model Router & HyDE
    participant BM25 as Okapi BM25 Lexical Index
    participant ColBERT as Binary ColBERT Vector Vault
    participant Graph as HyperGraph Traversal
    participant RRF as Reciprocal Rank Fusion (RRF)
    participant Cross as Cross-Encoder MaxSim Reranker
    participant Synth as LLM Synthesis Stream

    User->>Router: Search Query / Question
    Router->>Router: Sub-50ms HyDE Query Expansion (qwen2.5:0.5b)
    
    par Multi-Channel Search
        Router->>BM25: Lexical Search (SQLite FTS5 + Unicode NFC)
        Router->>ColBERT: Dense Semantic Retrieval (Embedding Dot Product)
        Router->>Graph: Multi-Hop Entity & Wikilink Traversal
    end

    BM25-->>RRF: Ranked Lexical Candidates
    ColBERT-->>RRF: Ranked Vector Candidates
    Graph-->>RRF: Ranked Graph Candidates

    RRF->>RRF: Multi-Channel Reciprocal Rank Fusion
    RRF->>Cross: Top 50 Unified Candidates
    Cross->>Cross: MaxSim Interaction Scoring & Temporal Decay
    Cross-->>Synth: Top K Grounded Context Chunks
    Synth-->>User: Streaming Response with Verified Citations`,steps:[{title:"Sub-50ms HyDE Expansion",desc:"Generates hypothetical document embeddings using the Micro model tier.",latency:"35ms"},{title:"Parallel 3-Channel Search",desc:"Simultaneously queries BM25 FTS5, ColBERT Vector Vault, and HyperGraph.",latency:"18ms"},{title:"Reciprocal Rank Fusion",desc:"Blends multiple candidate lists into a unified relevance ranking.",latency:"4ms"},{title:"Late Interaction MaxSim",desc:"Applies 64-bit binary ColBERT Hamming distance and temporal decay.",latency:"12ms"}]},{id:"privacy-soc2",title:"Zero-Knowledge Privacy & SOC 2 Compliance",subtitle:"Deterministic PII, Secret Key & HIPAA Medical Redaction",category:"SECURITY",icon:u,badge:"ZERO-KNOWLEDGE",badgeColor:"emerald",description:"Autonomous compliance inspector auditing all ingested content for emails, SSNs, JWT tokens, API keys, private keys, and HIPAA records with zero runtime bloat.",keyMetrics:[{label:"Secret Redaction",value:"100% Deterministic"},{label:"Security Score",value:"100.0% Trust"},{label:"Compliance",value:"SOC 2 Type II"},{label:"Dependencies",value:"0 (Stdlib)"}],mermaidCode:`graph TD
    InputText["Raw Document / Search Query"] --> Inspector["Privacy Compliance Inspector"]
    
    subgraph Inspection["Pattern Audit & Entity Identification"]
        PII1["Email Addresses ('RE_EMAIL')"]
        PII2["Social Security Numbers ('RE_SSN')"]
        PII3["Secret API Keys ('RE_API_KEY')"]
        PII4["JWT Bearer Tokens ('RE_JWT')"]
        PII5["Private Keys ('RE_PRIVATE_KEY')"]
        PII6["HIPAA Medical Identifiers"]
    end

    Inspector --> Inspection

    Inspection --> Masking{"Violations Found?"}
    Masking -->|Yes| Redaction["Deterministic Cryptographic Redaction"]
    Masking -->|No| CleanPass["Pass Content Unchanged"]

    Redaction --> VaultIndex[("SQLite Knowledge Vault Indexer")]
    CleanPass --> VaultIndex

    VaultIndex --> MerkleGen["Merkle Tree Root SHA-256 Engine"]
    MerkleGen --> Cert["SOC 2 Type II Cryptographic Attestation"]`,steps:[{title:"Pattern Auditing",desc:"Scans normalized NFC Unicode strings for secrets, PII, and medical terms.",latency:"2ms"},{title:"Deterministic Masking",desc:"Replaces sensitive entities with standardized cryptographically safe tokens.",latency:"1ms"},{title:"Merkle Tree Attestation",desc:"Hashes cleansed document chunks into the root verification block.",latency:"3ms"}]},{id:"sqlite-lifecycle",title:"Resilient SQLite WAL & Database Lifecycle",subtitle:"Corrupted Header Detection, Self-Healing & Thread Safety",category:"INFRASTRUCTURE",icon:p,badge:"SQLITE-WAL",badgeColor:"blue",description:"Robust database architecture featuring header corruption detection, FTS5 self-healing rebuilds, orphaned chunk pruning, and thread-local connection tracking.",keyMetrics:[{label:"Journal Mode",value:"WAL"},{label:"Busy Timeout",value:"5,000ms"},{label:"WinError 32 Prevention",value:"_local_connections"},{label:"Self-Healing",value:"Automated"}],mermaidCode:`stateDiagram-v2
    [*] --> DatabaseBoot: FastAPI Server Startup
    
    state DatabaseBoot {
        VerifyHeader: Inspect SQLite DB Header
        CheckFTS5: Validate FTS5 Virtual Table Parity
        ThreadRegistry: Initialize Global _local_connections
    }

    VerifyHeader --> CorruptionDetected: Header Corrupted / Unreadable
    CorruptionDetected --> ColdRestore: Automatic Backup Cold-Restore & Rebuild
    ColdRestore --> CheckFTS5

    VerifyHeader --> NormalBoot: Header Valid
    NormalBoot --> CheckFTS5
    CheckFTS5 --> ThreadRegistry

    state Operation {
        WALMode: PRAGMA journal_mode=WAL
        BusyTimeout: PRAGMA busy_timeout=5000
        Synchronous: PRAGMA synchronous=NORMAL
    }

    ThreadRegistry --> Operation`,steps:[{title:"Boot Integrity Check",desc:"Inspects SQLite database header and FTS5 virtual table synchronization.",latency:"5ms"},{title:"Thread-Local Registry",desc:"Maintains global registry of active connections for clean teardown.",latency:"<1ms"},{title:"Automatic Self-Healing",desc:"Prunes orphaned chunks and rebuilds desynchronized search indexes.",latency:"40ms"}]},{id:"p2p-sync",title:"Peer-to-Peer LAN Mesh Knowledge Replication",subtitle:"UDP Multicast Discovery & Vector Delta Synchronization",category:"INFRASTRUCTURE",icon:R,badge:"P2P-MESH",badgeColor:"amber",description:"Decentralized local-area knowledge sync enabling air-gapped nodes to exchange document vectors and Merkle differentials without cloud reliance.",keyMetrics:[{label:"Discovery Port",value:"UDP 8765 / 5353"},{label:"Diff Algorithm",value:"Merkle Set Diff"},{label:"Payload Format",value:"Compressed Zstandard"},{label:"Cloud Required",value:"0% (Air-Gapped)"}],mermaidCode:`sequenceDiagram
    autonumber
    participant NodeA as Node Alpha (Local Primary)
    participant Network as LAN Broadcast (UDP 8765)
    participant NodeB as Node Beta (Secondary Node)

    NodeA->>Network: UDP Beacon Announcement
    NodeB->>Network: UDP Beacon Announcement
    
    NodeA->>NodeB: TCP Connect (HTTP /api/p2p/handshake)
    NodeB-->>NodeA: Handshake Ack

    NodeA->>NodeB: GET /api/p2p/merkle-diff (Local Merkle Tree)
    NodeB->>NodeB: Calculate Set Difference (Missing Chunk Hashes)
    NodeB-->>NodeA: Delta Manifest (List of Missing Chunks)

    NodeA->>NodeB: POST /api/p2p/sync-payload (Compressed Chunk Stream)
    NodeB->>NodeB: Atomic SQLite Transaction (Insert Chunks & Vectors)
    NodeB-->>NodeA: Sync Acknowledged (100% Vector Parity Verified)`,steps:[{title:"Beacon Discovery",desc:"Broadcasts UDP heartbeat packets containing node identity and DB revision.",latency:"10ms"},{title:"Merkle Tree Differential",desc:"Computes hash differences between local and remote chunk trees.",latency:"25ms"},{title:"Atomic Vector Delta Stream",desc:"Transfers missing chunk BLOBs in compressed atomic transactions.",latency:"120ms"}]},{id:"frontend-topology",title:"React 19 Frontend SPA Component Topology",subtitle:"Vite 6 + Glassmorphic UI + Streaming LLM Telemetry",category:"TRI_ENGINE",icon:g,badge:"REACT-19",badgeColor:"purple",description:"Glassmorphic single-page architecture connecting 10 studio views with typed Fetch API streams, Server-Sent Events, and 3D knowledge graph visualizers.",keyMetrics:[{label:"UI Framework",value:"React 19.0.1"},{label:"Bundler",value:"Vite 6"},{label:"Active Views",value:"10 Studios"},{label:"Streaming Protocol",value:"SSE / Fetch Stream"}],mermaidCode:`graph TB
    subgraph FrontendSPA["React 19 SPA Frontend (Vite)"]
        App["App Root Container"]
        NavBar["Glassmorphic Navigation Bar"]
        
        subgraph Views["Active Studio Views"]
            V1["Dashboard & Health Metrics View"]
            V2["Interactive Chat Studio (Streaming LLM)"]
            V3["Workspace Document Manager"]
            V4["Knowledge Search & Filter Explorer"]
            V5["Document Ingestion & Dropzone Pipeline"]
            V6["2D/3D Knowledge Graph Visualizer"]
            V7["System Config & Orchestration Studio"]
            V8["Settings, Backups & Maintenance"]
            V9["Universal Crawler & Legal Studio"]
            V10["EPUB Reader & Document Studio"]
        end

        App --> NavBar
        NavBar --> Views
    end

    subgraph BackendAPI["FastAPI Backend (/api)"]
        R_Chat["/api/chat/*"]
        R_Search["/api/search/*"]
        R_File["/api/file/*"]
        R_Crawler["/api/crawler/*"]
        R_Graph["/api/graph/*"]
        R_System["/api/system/*"]
    end

    BackendAPI --> HardwareLocal["Local Hardware & Ollama Daemon"]`,steps:[{title:"Component Mount",desc:"Initializes theme context, active workspace, and hash routing.",latency:"4ms"},{title:"Stream Connection",desc:"Opens bidirectional SSE stream to FastAPI backend for live token generation.",latency:"12ms"},{title:"WebGL Render",desc:"Renders 3D force-directed knowledge graph in WebGL context.",latency:"16ms"}]}];function D(){const[c,x]=o.useState("tri-engine"),[a,n]=o.useState("visual"),[d,m]=o.useState(!1),{addToast:h}=S(),r=i.find(t=>t.id===c)||i[0],b=()=>{navigator.clipboard.writeText(r.mermaidCode),m(!0),h("Mermaid diagram code copied to clipboard!","success"),setTimeout(()=>m(!1),2e3)},y=t=>{switch(t){case"emerald":return"bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border-emerald-500/30";case"amber":return"bg-amber-500/15 text-amber-600 dark:text-amber-400 border-amber-500/30";case"blue":return"bg-blue-500/15 text-blue-600 dark:text-blue-400 border-blue-500/30";case"purple":return"bg-purple-500/15 text-purple-600 dark:text-purple-400 border-purple-500/30"}};return e.jsxs("div",{className:"h-full flex flex-col overflow-hidden bg-slate-950/40 text-slate-100 p-6 space-y-6",children:[e.jsxs("div",{className:"flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-white/5",children:[e.jsx("div",{className:"space-y-1",children:e.jsxs("div",{className:"flex items-center gap-3",children:[e.jsx("div",{className:"w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500/20 to-teal-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 shadow-lg shadow-emerald-500/10",children:e.jsx(g,{className:"w-5 h-5"})}),e.jsxs("div",{children:[e.jsxs("h1",{className:"text-2xl font-bold font-serif-claude text-slate-100 flex items-center gap-2",children:["System Architecture & Topology Visualizer",e.jsx("span",{className:"px-2 py-0.5 text-xs font-mono rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20",children:"v3.2.0 Active"})]}),e.jsx("p",{className:"text-xs text-slate-400",children:"Interactive architectural models, multi-bridge execution pipelines, and cryptographic trust controls."})]})]})}),e.jsxs("div",{className:"flex items-center gap-3",children:[e.jsxs("div",{className:"px-3 py-1.5 rounded-xl bg-slate-900/80 border border-white/10 flex items-center gap-2 text-xs font-mono",children:[e.jsx(u,{className:"w-4 h-4 text-emerald-400"}),e.jsx("span",{className:"text-slate-300",children:"SOC 2 Type II:"}),e.jsx("span",{className:"text-emerald-400 font-semibold",children:"CERTIFIED"})]}),e.jsxs("div",{className:"px-3 py-1.5 rounded-xl bg-slate-900/80 border border-white/10 flex items-center gap-2 text-xs font-mono",children:[e.jsx(N,{className:"w-4 h-4 text-emerald-400"}),e.jsx("span",{className:"text-slate-300",children:"Clean Arch:"}),e.jsx("span",{className:"text-emerald-400 font-semibold",children:"100% (A+)"})]})]})]}),e.jsxs("div",{className:"flex-1 grid grid-cols-1 lg:grid-cols-12 gap-6 min-h-0",children:[e.jsxs("div",{className:"lg:col-span-4 flex flex-col space-y-3 min-h-0",children:[e.jsxs("div",{className:"flex items-center justify-between px-2",children:[e.jsx("span",{className:"text-xs font-semibold uppercase tracking-wider text-slate-400",children:"Subsystem Topologies"}),e.jsxs("span",{className:"text-xs font-mono text-slate-500",children:[i.length," Models"]})]}),e.jsx("div",{className:"flex-1 overflow-y-auto space-y-2 pr-1 custom-scrollbar",children:i.map(t=>{const s=t.icon,l=c===t.id;return e.jsxs("button",{onClick:()=>x(t.id),className:`w-full text-left p-3.5 rounded-2xl border transition-all duration-200 flex items-start gap-3.5 ${l?"bg-slate-900/90 border-emerald-500/40 shadow-lg shadow-emerald-500/5":"bg-slate-900/40 hover:bg-slate-900/70 border-white/5 hover:border-white/10"}`,children:[e.jsx("div",{className:`p-2 rounded-xl border mt-0.5 ${l?"bg-emerald-500/20 border-emerald-500/30 text-emerald-400":"bg-slate-800/50 border-white/5 text-slate-400"}`,children:e.jsx(s,{className:"w-4 h-4"})}),e.jsxs("div",{className:"flex-1 min-w-0",children:[e.jsx("div",{className:"flex items-center justify-between gap-2",children:e.jsx("h3",{className:`text-sm font-medium truncate ${l?"text-emerald-300 font-semibold":"text-slate-200"}`,children:t.title})}),e.jsx("p",{className:"text-xs text-slate-400 truncate mt-0.5",children:t.subtitle}),e.jsx("div",{className:"flex items-center gap-2 mt-2",children:e.jsx("span",{className:`px-2 py-0.5 text-[10px] font-mono rounded-full border ${y(t.badgeColor)}`,children:t.badge})})]})]},t.id)})})]}),e.jsxs("div",{className:"lg:col-span-8 flex flex-col bg-slate-900/60 border border-white/10 rounded-2xl overflow-hidden shadow-2xl min-h-0",children:[e.jsxs("div",{className:"p-4 bg-slate-900/90 border-b border-white/10 flex flex-wrap items-center justify-between gap-3",children:[e.jsxs("div",{children:[e.jsx("h2",{className:"text-base font-bold font-serif-claude text-slate-100 flex items-center gap-2",children:r.title}),e.jsx("p",{className:"text-xs text-slate-400 mt-0.5",children:r.description})]}),e.jsxs("div",{className:"flex items-center gap-2",children:[e.jsxs("div",{className:"p-1 bg-slate-950/80 rounded-xl border border-white/10 flex items-center gap-1",children:[e.jsx("button",{onClick:()=>n("visual"),className:`px-3 py-1 text-xs font-medium rounded-lg transition-all ${a==="visual"?"bg-emerald-600 text-white shadow-md":"text-slate-400 hover:text-slate-200"}`,children:"Pipeline Flow"}),e.jsx("button",{onClick:()=>n("mermaid"),className:`px-3 py-1 text-xs font-medium rounded-lg transition-all ${a==="mermaid"?"bg-emerald-600 text-white shadow-md":"text-slate-400 hover:text-slate-200"}`,children:"Mermaid Source"}),e.jsx("button",{onClick:()=>n("specs"),className:`px-3 py-1 text-xs font-medium rounded-lg transition-all ${a==="specs"?"bg-emerald-600 text-white shadow-md":"text-slate-400 hover:text-slate-200"}`,children:"SLA Specs"})]}),e.jsxs("button",{onClick:b,className:"p-2 rounded-xl bg-slate-800/80 hover:bg-slate-700 text-slate-300 hover:text-white border border-white/10 transition-colors flex items-center gap-1.5 text-xs",title:"Copy Mermaid Code",children:[d?e.jsx(A,{className:"w-3.5 h-3.5 text-emerald-400"}):e.jsx(k,{className:"w-3.5 h-3.5"}),e.jsx("span",{children:d?"Copied":"Copy"})]})]})]}),e.jsx("div",{className:"grid grid-cols-2 md:grid-cols-4 gap-3 p-4 bg-slate-950/50 border-b border-white/5",children:r.keyMetrics.map((t,s)=>e.jsxs("div",{className:"p-2.5 rounded-xl bg-slate-900/60 border border-white/5 text-center",children:[e.jsx("span",{className:"text-[11px] uppercase tracking-wider font-mono text-slate-400 block",children:t.label}),e.jsx("span",{className:"text-sm font-bold font-mono text-emerald-400 mt-0.5 block",children:t.value})]},s))}),e.jsxs("div",{className:"flex-1 p-6 overflow-y-auto custom-scrollbar",children:[a==="visual"&&e.jsxs("div",{className:"space-y-6",children:[e.jsxs("div",{className:"space-y-3",children:[e.jsx("span",{className:"text-xs font-semibold uppercase tracking-wider text-slate-400 block",children:"Execution Flow & Sequence Stages"}),e.jsx("div",{className:"space-y-3",children:r.steps.map((t,s)=>e.jsxs("div",{className:"p-4 rounded-xl bg-slate-950/60 border border-white/5 flex items-start gap-4",children:[e.jsx("div",{className:"w-7 h-7 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-mono text-xs font-bold flex items-center justify-center flex-shrink-0 mt-0.5",children:s+1}),e.jsxs("div",{className:"flex-1 min-w-0",children:[e.jsxs("div",{className:"flex items-center justify-between gap-2",children:[e.jsx("h4",{className:"text-sm font-semibold text-slate-200",children:t.title}),t.latency&&e.jsx("span",{className:"text-[11px] font-mono px-2 py-0.5 rounded-md bg-emerald-500/10 text-emerald-400 border border-emerald-500/20",children:t.latency})]}),e.jsx("p",{className:"text-xs text-slate-400 mt-1",children:t.desc})]})]},s))})]}),e.jsxs("div",{className:"p-4 rounded-xl bg-slate-950/40 border border-white/5 text-xs text-slate-400 space-y-2",children:[e.jsxs("div",{className:"flex items-center gap-2 text-slate-300 font-semibold",children:[e.jsx(T,{className:"w-4 h-4 text-emerald-400"}),e.jsx("span",{children:"Architectural Guarantee"})]}),e.jsx("p",{children:"All operations within this subsystem are executed strictly in-process with zero external cloud API dependencies, enforcing single-node air-gapped data residency and SOC 2 Type II attestation."})]})]}),a==="mermaid"&&e.jsxs("div",{className:"h-full flex flex-col space-y-2",children:[e.jsxs("div",{className:"flex items-center justify-between",children:[e.jsx("span",{className:"text-xs font-mono text-slate-400",children:"Mermaid.js Diagram Definition"}),e.jsx("span",{className:"text-[11px] font-mono text-slate-500",children:"GitHub Flavored Markdown Compatible"})]}),e.jsx("pre",{className:"flex-1 p-4 rounded-xl bg-slate-950 border border-white/10 font-mono text-xs text-emerald-300 overflow-x-auto selection:bg-emerald-900 selection:text-white leading-relaxed",children:r.mermaidCode})]}),a==="specs"&&e.jsx("div",{className:"space-y-4 text-xs",children:e.jsxs("div",{className:"p-4 rounded-xl bg-slate-950/60 border border-white/5 space-y-3",children:[e.jsxs("h4",{className:"text-sm font-semibold text-slate-200 flex items-center gap-2",children:[e.jsx(w,{className:"w-4 h-4 text-amber-400"}),e.jsx("span",{children:"Technical & Performance Specifications"})]}),e.jsxs("div",{className:"grid grid-cols-1 md:grid-cols-2 gap-3 text-slate-300",children:[e.jsxs("div",{className:"p-3 rounded-lg bg-slate-900/60 border border-white/5",children:[e.jsx("span",{className:"text-slate-400 block mb-1 font-mono uppercase text-[10px]",children:"Processing Model"}),e.jsx("span",{className:"font-semibold text-slate-200",children:"Asynchronous Parallel DAG / In-Memory Queue"})]}),e.jsxs("div",{className:"p-3 rounded-lg bg-slate-900/60 border border-white/5",children:[e.jsx("span",{className:"text-slate-400 block mb-1 font-mono uppercase text-[10px]",children:"Failure Domain"}),e.jsx("span",{className:"font-semibold text-slate-200",children:"Non-Crashing Try/Except Import Guards & Auto-Rollback"})]}),e.jsxs("div",{className:"p-3 rounded-lg bg-slate-900/60 border border-white/5",children:[e.jsx("span",{className:"text-slate-400 block mb-1 font-mono uppercase text-[10px]",children:"Memory Footprint"}),e.jsx("span",{className:"font-semibold text-slate-200",children:"< 490 MB VRAM (Single-Instance Model Isolation)"})]}),e.jsxs("div",{className:"p-3 rounded-lg bg-slate-900/60 border border-white/5",children:[e.jsx("span",{className:"text-slate-400 block mb-1 font-mono uppercase text-[10px]",children:"Audit Compliance"}),e.jsx("span",{className:"font-semibold text-slate-200",children:"SOC 2 Type II Merkle Root SHA-256 Provenance"})]})]})]})})]})]})]})]})}export{D as default};
