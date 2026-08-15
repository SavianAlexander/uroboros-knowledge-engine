import json
from typing import List, Dict, Any

"""
Standalone Interactive HTML5 Knowledge Vault Topology Visualizer.
Generates an offline-first, dependency-free glassmorphic HTML5 interactive canvas
with 2D physics, node drag-and-drop, statutory inspectors, and live RAG search.
"""

class KnowledgeVaultVisualizer:
    """Generates self-contained interactive HTML5 Knowledge Vault Visualizers."""

    @classmethod
    def generate_html(cls, job_name: str, documents: List[Dict[str, Any]], concordance: Dict[str, Any]) -> str:
        """Compile documents, entities, and concordance into an interactive HTML application."""
        nodes = []
        edges = []
        node_map = {}

        # 1. Build Visual Nodes
        for d in documents:
            doc_id = f"d_{d.get('id', hash(d.get('url', '')))}"
            doc_title = d.get("title", "Document")
            node_map[doc_id] = len(nodes)
            nodes.append({
                "id": doc_id,
                "label": doc_title[:32],
                "full_title": doc_title,
                "type": "document",
                "url": d.get("url", ""),
                "size": 14,
                "color": "#38bdf8", # Sky Blue
                "content": d.get("content_text", "")[:300] + "..."
            })

            # Entities as Concept Nodes
            ent_json = d.get("entities_json", "{}")
            ent_data = json.loads(ent_json) if isinstance(ent_json, str) else (ent_json or {})
            for e_type, e_list in ent_data.items():
                for e in e_list:
                    e_id = f"e_{hash(e)}"
                    if e_id not in node_map:
                        node_map[e_id] = len(nodes)
                        color = "#a855f7" if e_type == "leyes" else ("#10b981" if e_type == "agencias" else "#f59e0b")
                        nodes.append({
                            "id": e_id,
                            "label": e[:24],
                            "full_title": e,
                            "type": e_type,
                            "url": "",
                            "size": 10 if e_type != "leyes" else 12,
                            "color": color,
                            "content": f"Entity Category: {e_type.upper()}"
                        })
                    edges.append({"source": node_map[doc_id], "target": node_map[e_id], "label": "mentions"})

            # Triplets as Concept Edges
            trip_json = d.get("triplets_json", "[]")
            trip_list = json.loads(trip_json) if isinstance(trip_json, str) else (trip_json or [])
            for t in trip_list:
                s_id = f"e_{hash(t['subject'])}"
                o_id = f"e_{hash(t['object'])}"
                if s_id in node_map and o_id in node_map:
                    edges.append({"source": node_map[s_id], "target": node_map[o_id], "label": t['predicate']})

        nodes_json = json.dumps(nodes, ensure_ascii=False)
        edges_json = json.dumps(edges, ensure_ascii=False)
        concordance_json = json.dumps(concordance, ensure_ascii=False)

        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{job_name} - Sovereign Knowledge Vault</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
        body {{ background: #0b0f19; color: #f3f4f6; overflow: hidden; height: 100vh; display: flex; flex-direction: column; }}
        header {{ background: rgba(17, 24, 39, 0.85); backdrop-filter: blur(12px); border-bottom: 1px solid rgba(255,255,255,0.08); padding: 14px 24px; display: flex; justify-content: space-between; align-items: center; z-index: 10; }}
        .title-area h1 {{ font-size: 1.15rem; font-weight: 700; color: #38bdf8; display: flex; align-items: center; gap: 8px; }}
        .title-area p {{ font-size: 0.8rem; color: #9ca3af; }}
        .controls {{ display: flex; gap: 12px; align-items: center; }}
        input.search {{ background: rgba(31, 41, 55, 0.7); border: 1px solid rgba(255,255,255,0.12); color: #fff; padding: 7px 14px; border-radius: 8px; font-size: 0.85rem; outline: none; width: 220px; }}
        input.search:focus {{ border-color: #38bdf8; }}
        .btn {{ background: #1e293b; border: 1px solid rgba(255,255,255,0.1); color: #e2e8f0; padding: 7px 14px; border-radius: 8px; font-size: 0.8rem; cursor: pointer; transition: all 0.2s; }}
        .btn:hover {{ background: #334155; color: #38bdf8; }}
        .main-container {{ flex: 1; display: flex; position: relative; }}
        #canvas {{ flex: 1; width: 100%; height: 100%; display: block; }}
        .sidebar {{ width: 340px; background: rgba(15, 23, 42, 0.92); backdrop-filter: blur(16px); border-left: 1px solid rgba(255,255,255,0.08); padding: 20px; overflow-y: auto; z-index: 5; display: flex; flex-direction: column; gap: 16px; }}
        .sidebar h2 {{ font-size: 1rem; color: #f8fafc; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 8px; }}
        .badge {{ display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; }}
        .badge.document {{ background: rgba(56, 189, 248, 0.2); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.4); }}
        .badge.leyes {{ background: rgba(168, 85, 247, 0.2); color: #a855f7; border: 1px solid rgba(168, 85, 247, 0.4); }}
        .badge.agencias {{ background: rgba(16, 185, 129, 0.2); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.4); }}
        .snippet-box {{ background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(255,255,255,0.06); padding: 12px; border-radius: 8px; font-size: 0.82rem; color: #cbd5e1; line-height: 1.45; }}
        .legend {{ position: absolute; bottom: 20px; left: 20px; background: rgba(15, 23, 42, 0.85); backdrop-filter: blur(8px); border: 1px solid rgba(255,255,255,0.08); padding: 12px 16px; border-radius: 8px; font-size: 0.78rem; display: flex; gap: 14px; z-index: 5; }}
        .legend-item {{ display: flex; align-items: center; gap: 6px; }}
        .dot {{ width: 10px; height: 10px; border-radius: 50%; display: inline-block; }}
    </style>
</head>
<body>
    <header>
        <div class="title-area">
            <h1>⬡ {job_name}</h1>
            <p>Sovereign Knowledge Vault Interactive Topology</p>
        </div>
        <div class="controls">
            <input type="text" id="search" class="search" placeholder="Filter entities / statutes...">
            <button class="btn" onclick="resetView()">Reset View</button>
        </div>
    </header>

    <div class="main-container">
        <canvas id="canvas"></canvas>
        <div class="legend">
            <div class="legend-item"><span class="dot" style="background:#38bdf8;"></span> Document</div>
            <div class="legend-item"><span class="dot" style="background:#a855f7;"></span> Statute / Ley</div>
            <div class="legend-item"><span class="dot" style="background:#10b981;"></span> Agency / Authority</div>
            <div class="legend-item"><span class="dot" style="background:#f59e0b;"></span> Concept</div>
        </div>
        <div class="sidebar" id="sidebar">
            <h2>Node Inspector</h2>
            <p style="font-size:0.85rem; color:#94a3b8;">Click any node in the knowledge graph to inspect cross-statutory citations, lifecycle status, and RAG context.</p>
            <div id="inspector-content" style="display:none; flex-direction:column; gap:12px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span id="node-type" class="badge"></span>
                </div>
                <h3 id="node-title" style="font-size:1.1rem; color:#fff;"></h3>
                <a id="node-link" href="#" target="_blank" style="font-size:0.78rem; color:#38bdf8; text-decoration:none; word-break:break-all;"></a>
                <div class="snippet-box" id="node-content"></div>
            </div>
        </div>
    </div>

    <script>
        const rawNodes = {nodes_json};
        const rawEdges = {edges_json};
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');

        let width = canvas.width = window.innerWidth - 340;
        let height = canvas.height = window.innerHeight - 60;
        window.addEventListener('resize', () => {{
            width = canvas.width = window.innerWidth - 340;
            height = canvas.height = window.innerHeight - 60;
        }});

        // Physics Initialization
        const nodes = rawNodes.map((n, i) => ({{
            ...n,
            x: width / 2 + (Math.random() - 0.5) * width * 0.7,
            y: height / 2 + (Math.random() - 0.5) * height * 0.7,
            vx: 0,
            vy: 0
        }}));

        let transform = {{ x: 0, y: 0, k: 1 }};
        let draggedNode = null;
        let selectedNode = null;

        // Force Simulation Step
        function updatePhysics() {{
            // Repulsion
            for (let i = 0; i < nodes.length; i++) {{
                for (let j = i + 1; j < nodes.length; j++) {{
                    const dx = nodes[j].x - nodes[i].x;
                    const dy = nodes[j].y - nodes[i].y;
                    const dist = Math.hypot(dx, dy) || 1;
                    if (dist < 180) {{
                        const force = (180 - dist) / dist * 0.4;
                        nodes[i].vx -= dx * force;
                        nodes[i].vy -= dy * force;
                        nodes[j].vx += dx * force;
                        nodes[j].vy += dy * force;
                    }}
                }}
            }}

            // Attraction along edges
            for (const e of rawEdges) {{
                const s = nodes[e.source];
                const t = nodes[e.target];
                if (!s || !t) continue;
                const dx = t.x - s.x;
                const dy = t.y - s.y;
                const dist = Math.hypot(dx, dy) || 1;
                const force = (dist - 90) * 0.008;
                s.vx += dx * force;
                s.vy += dy * force;
                t.vx -= dx * force;
                t.vy -= dy * force;
            }}

            // Center gravity & damping
            for (const n of nodes) {{
                if (n === draggedNode) continue;
                n.vx += (width / 2 - n.x) * 0.0005;
                n.vy += (height / 2 - n.y) * 0.0005;
                n.x += n.vx;
                n.y += n.vy;
                n.vx *= 0.88;
                n.vy *= 0.88;
            }}
        }}

        function draw() {{
            ctx.save();
            ctx.clearRect(0, 0, width, height);
            ctx.translate(transform.x, transform.y);
            ctx.scale(transform.k, transform.k);

            // Draw Edges
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
            ctx.lineWidth = 1;
            for (const e of rawEdges) {{
                const s = nodes[e.source];
                const t = nodes[e.target];
                if (!s || !t) continue;
                ctx.beginPath();
                ctx.moveTo(s.x, s.y);
                ctx.lineTo(t.x, t.y);
                ctx.stroke();
            }}

            // Draw Nodes
            for (const n of nodes) {{
                ctx.beginPath();
                ctx.arc(n.x, n.y, n.size, 0, Math.PI * 2);
                ctx.fillStyle = n.color;
                ctx.fill();

                if (n === selectedNode) {{
                    ctx.strokeStyle = '#fff';
                    ctx.lineWidth = 2.5;
                    ctx.stroke();
                }}

                // Labels
                ctx.font = '10px -apple-system, sans-serif';
                ctx.fillStyle = '#cbd5e1';
                ctx.textAlign = 'center';
                ctx.fillText(n.label, n.x, n.y + n.size + 12);
            }}
            ctx.restore();

            updatePhysics();
            requestAnimationFrame(draw);
        }}
        requestAnimationFrame(draw);

        // Interaction Handlers
        let isPanning = false;
        let startX, startY;

        canvas.addEventListener('mousedown', (e) => {{
            const mouseX = (e.clientX - transform.x) / transform.k;
            const mouseY = (e.clientY - transform.y - 60) / transform.k;

            for (let i = nodes.length - 1; i >= 0; i--) {{
                const n = nodes[i];
                if (Math.hypot(n.x - mouseX, n.y - mouseY) < n.size + 5) {{
                    draggedNode = n;
                    selectNode(n);
                    return;
                }}
            }}
            isPanning = true;
            startX = e.clientX - transform.x;
            startY = e.clientY - transform.y;
        }});

        window.addEventListener('mousemove', (e) => {{
            if (draggedNode) {{
                draggedNode.x = (e.clientX - transform.x) / transform.k;
                draggedNode.y = (e.clientY - transform.y - 60) / transform.k;
            }} else if (isPanning) {{
                transform.x = e.clientX - startX;
                transform.y = e.clientY - startY;
            }}
        }});

        window.addEventListener('mouseup', () => {{
            draggedNode = null;
            isPanning = false;
        }});

        canvas.addEventListener('wheel', (e) => {{
            e.preventDefault();
            const factor = e.deltaY < 0 ? 1.1 : 0.9;
            transform.k = Math.max(0.2, Math.min(3.0, transform.k * factor));
        }});

        function selectNode(n) {{
            selectedNode = n;
            document.getElementById('inspector-content').style.display = 'flex';
            const badge = document.getElementById('node-type');
            badge.innerText = n.type;
            badge.className = 'badge ' + (n.type in {{document:1, leyes:1, agencias:1}} ? n.type : 'document');
            document.getElementById('node-title').innerText = n.full_title;
            const link = document.getElementById('node-link');
            if (n.url) {{
                link.href = n.url;
                link.innerText = n.url;
                link.style.display = 'block';
            }} else {{
                link.style.display = 'none';
            }}
            document.getElementById('node-content').innerText = n.content || 'No text snippet available.';
        }}

        function resetView() {{
            transform = {{ x: 0, y: 0, k: 1 }};
        }}

        document.getElementById('search').addEventListener('input', (e) => {{
            const q = e.target.value.toLowerCase();
            if (!q) return;
            const match = nodes.find(n => n.full_title.toLowerCase().includes(q));
            if (match) {{
                selectNode(match);
                transform.x = width / 2 - match.x * transform.k;
                transform.y = height / 2 - match.y * transform.k + 60;
            }}
        }});
    </script>
</body>
</html>
"""
        return html_template
