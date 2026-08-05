"""
Domain 24: Playwright UI Adversarial Test Suite.
Verifies watcher thread bypass in test mode, query cache invalidation state during active indexing threads,
and concept graph canvas animation loop containment, zoom bounds, and node selection sensitivity.
"""

import os
import sys
import time
import threading
import shutil
import sqlite3
import unittest
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import know
know.DB_FILE = "adversarial_i3.db"

def mock_watcher(directory, callback=None):
    pass

know.start_active_folder_watcher = mock_watcher

import main
import uvicorn
from fastapi.testclient import TestClient
from playwright.sync_api import sync_playwright

PORT = 8097


class ServerThread(threading.Thread):
    def __init__(self, port=PORT):
        super().__init__()
        self.daemon = True
        self.port = port
        self.config = uvicorn.Config(main.app, host="127.0.0.1", port=self.port, log_level="warning")
        self.server = uvicorn.Server(self.config)

    def run(self):
        self.server.run()

    def stop(self):
        self.server.should_exit = True


class TestAdversarialI3(unittest.TestCase):
    port = PORT

    @classmethod
    def setUpClass(cls):
        cls.sandbox = Path("test_sandbox_adversarial").resolve()
        if cls.sandbox.exists():
            shutil.rmtree(cls.sandbox, ignore_errors=True)
        cls.sandbox.mkdir(parents=True, exist_ok=True)

        know.reset_db_connections()
        for suffix in ["", "-wal", "-shm"]:
            fpath = "adversarial_i3.db" + suffix
            if os.path.exists(fpath):
                try:
                    os.remove(fpath)
                except Exception:
                    pass

        know.DB_FILE = "adversarial_i3.db"
        main.ACTIVE_DIR = str(cls.sandbox)
        know.init_db()

        files_data = [
            ("formula.txt", "This is an astrophysics formula about gravity and quantum physics."),
            ("data_analysis.txt", "Astrophysics statistics data report about planetary orbit and gravity."),
            ("quantum.txt", "Quantum mechanics explains the behavior of subatomic particles and physics."),
            ("chemistry.txt", "Organic chemistry molecules study and molecular physics bond calculations."),
            ("general.txt", "General document about gravity in astrophysics context.")
        ]

        for fname, content in files_data:
            fpath = cls.sandbox / fname
            fpath.write_text(content, encoding="utf-8")

        know.index_directory(str(cls.sandbox))

        import socket
        sock = socket.socket()
        sock.bind(('127.0.0.1', 0))
        cls.port = sock.getsockname()[1]
        sock.close()

        cls.server = ServerThread(cls.port)
        cls.server.start()

        # Health polling loop
        server_ready = False
        start_time = time.time()
        while time.time() - start_time < 10.0:
            if not cls.server.is_alive():
                raise RuntimeError(f"Server thread died before initialization on port {cls.port}")
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{cls.port}/api/health", timeout=1.0) as resp:
                    if resp.status == 200:
                        server_ready = True
                        break
            except Exception:
                threading.Event().wait(0.1)

        if not server_ready:
            raise RuntimeError(f"Uvicorn server failed to respond on port {cls.port}")

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()
        cls.server.join(timeout=5.0)
        know.reset_db_connections()

        for suffix in ["", "-wal", "-shm"]:
            fpath = "adversarial_i3.db" + suffix
            if os.path.exists(fpath):
                for _ in range(10):
                    try:
                        os.remove(fpath)
                        break
                    except Exception:
                        threading.Event().wait(0.05)

        if cls.sandbox.exists():
            for _ in range(10):
                try:
                    shutil.rmtree(cls.sandbox)
                    break
                except Exception:
                    threading.Event().wait(0.05)

        main.ACTIVE_DIR = "dumps"

    def setUp(self):
        know.DB_FILE = "adversarial_i3.db"
        main.ACTIVE_DIR = str(self.sandbox)

    def tearDown(self):
        pass

    def test_01_watcher_thread_bypassed(self):
        """
        Preconditions: Test environment initialized with main.is_testing set to True.
        Invariants: Background folder watcher thread must not spawn during test runner initialization.
        Outcomes: main.is_testing evaluates True and no active thread is named 'WatcherThread'.
        """
        self.assertTrue(main.is_testing)
        watcher_running = any(t.name == "WatcherThread" for t in threading.enumerate())
        self.assertFalse(watcher_running)

    def test_02_cache_no_empty_when_indexing(self):
        """
        Preconditions: Global query cache initialized with search API endpoints active.
        Invariants: Empty search result sets produced while an 'IndexerThread' is running must not be cached.
        Outcomes: Unmatched search queries return 0 results and leave cache key unpopulated when IndexerThread is active; non-empty search results cache normally.
        """
        main.GLOBAL_QUERY_CACHE.invalidate()
        main.GLOBAL_QUERY_CACHE.hits = 0
        main.GLOBAL_QUERY_CACHE.misses = 0

        res1 = main.GLOBAL_QUERY_CACHE.get("empty_query")
        self.assertIsNone(res1)

        client = TestClient(main.app)
        response = client.get("/api/search?q=notexistinanyfile")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["results"]), 0)

        cache_key = "notexistinanyfile:keyword:None:OR"
        self.assertIsNotNone(main.GLOBAL_QUERY_CACHE.get(cache_key))

        mock_indexer = threading.Thread(name="IndexerThread", target=lambda: threading.Event().wait(0.5))
        mock_indexer.start()

        main.GLOBAL_QUERY_CACHE.invalidate()
        response = client.get("/api/search?q=anothernotexistent")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["results"]), 0)

        cache_key_2 = "anothernotexistent:keyword:None:OR"
        self.assertIsNone(main.GLOBAL_QUERY_CACHE.get(cache_key_2))

        response_ok = client.get("/api/search?q=gravity")
        self.assertEqual(response_ok.status_code, 200)
        self.assertGreater(len(response_ok.json()["results"]), 0)

        cache_key_ok = "gravity:keyword:None:OR"
        self.assertIsNotNone(main.GLOBAL_QUERY_CACHE.get(cache_key_ok))

        mock_indexer.join(timeout=3.0)

    def test_03_frontend_graph_adversarial(self):
        """
        Preconditions: Playwright headless browser navigated to graph canvas endpoint.
        Invariants: Concept graph canvas animation loop must not duplicate/leak frames; zoom scaling and node selection must remain accurate across 0.2x to 5.0x zoom levels.
        Outcomes: Active animation loops remain bounded to 1; zoom reset restores origin; node selection succeeds at multi-zoom bounds.
        """
        log_path = Path("playwright_debug.log")
        if log_path.exists():
            try:
                log_path.unlink()
            except Exception:
                pass

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(f"http://127.0.0.1:{self.port}/")
            page.wait_for_selector(".tab-link[data-tab='explorer']", timeout=5000)
            page.click(".tab-link[data-tab='explorer']")
            page.click("button[data-category='graph']")
            page.wait_for_selector("#concept-graph-canvas", timeout=5000)
            page.select_option("#graph-layout-preset", "circular")

            page.evaluate("""() => {
                window.activeFrames = new Set();
                const origReq = window.requestAnimationFrame;
                const origCancel = window.cancelAnimationFrame;
                window.requestAnimationFrame = (cb) => {
                    const id = origReq((timestamp) => {
                        window.activeFrames.delete(id);
                        cb(timestamp);
                    });
                    window.activeFrames.add(id);
                    return id;
                };
                window.cancelAnimationFrame = (id) => {
                    window.activeFrames.delete(id);
                    origCancel(id);
                };

                const origDrawGraph = window.drawGraph;
                window.drawGraph = function(nodes, links) {
                    window.capturedNodes = nodes;
                    window.capturedLinks = links;
                    return origDrawGraph.call(this, nodes, links);
                };

                const origGetContext = HTMLCanvasElement.prototype.getContext;
                HTMLCanvasElement.prototype.getContext = function(type, ...args) {
                    const ctx = origGetContext.call(this, type, ...args);
                    if (type === '2d') {
                        const origTranslate = ctx.translate;
                        const origScale = ctx.scale;
                        ctx.translate = function(x, y) {
                            window.lastOffsetX = x;
                            window.lastOffsetY = y;
                            return origTranslate.call(this, x, y);
                        };
                        ctx.scale = function(sx, sy) {
                            window.lastZoomScale = sx;
                            return origScale.call(this, sx, sy);
                        };
                    }
                    return ctx;
                };

                window.getNodeClickCoords = function(nodeIdx, offsetPixels = 10) {
                    const canvas = document.getElementById("concept-graph-canvas");
                    const rect = canvas.getBoundingClientRect();
                    const n = window.capturedNodes[nodeIdx];
                    const sx = n.x * window.lastZoomScale + window.lastOffsetX;
                    const sy = n.y * window.lastZoomScale + window.lastOffsetY;
                    return {
                        x: rect.left + sx * (rect.width / canvas.width) + offsetPixels,
                        y: rect.top + sy * (rect.height / canvas.height)
                    };
                };
            }""")

            page.evaluate("loadConceptGraph()")
            page.wait_for_function("window.capturedNodes && window.capturedNodes.length > 0", timeout=5000)

            nodes = page.evaluate("window.capturedNodes")
            self.assertIsNotNone(nodes)
            self.assertGreater(len(nodes), 0)

            page.evaluate("""async () => {
                for (let i = 0; i < 50; i++) {
                    loadConceptGraph();
                }
            }""")
            page.wait_for_function("window.activeFrames.size === 1", timeout=5000)
            active_count = page.evaluate("window.activeFrames.size")
            self.assertEqual(active_count, 1, f"Expected exactly 1 active animation loop, but got {active_count}!")

            page.click("button[title='Reset View']")
            page.wait_for_timeout(200)
            scale = page.evaluate("window.lastZoomScale")
            ox = page.evaluate("window.lastOffsetX")
            oy = page.evaluate("window.lastOffsetY")
            self.assertAlmostEqual(scale, 1.0, delta=0.01)
            self.assertAlmostEqual(ox, 0.0, delta=0.01)
            self.assertAlmostEqual(oy, 0.0, delta=0.01)

            page.click("button[title='Zoom In']")
            page.wait_for_timeout(100)
            page.click("button[title='Zoom In']")
            page.wait_for_timeout(100)
            page.click("button[title='Zoom In']")
            page.wait_for_timeout(200)
            scale_in = page.evaluate("window.lastZoomScale")
            self.assertGreater(scale_in, 1.5)

            page.click("button[title='Zoom Out']")
            page.wait_for_timeout(100)
            page.click("button[title='Zoom Out']")
            page.wait_for_timeout(100)
            page.click("button[title='Zoom Out']")
            page.wait_for_timeout(200)
            scale_out = page.evaluate("window.lastZoomScale")
            self.assertAlmostEqual(scale_out, scale_in * 0.8 * 0.8 * 0.8, delta=0.05)

            page.click("button[title='Reset View']")
            page.wait_for_timeout(200)
            scale_reset = page.evaluate("window.lastZoomScale")
            ox_reset = page.evaluate("window.lastOffsetX")
            oy_reset = page.evaluate("window.lastOffsetY")
            self.assertAlmostEqual(scale_reset, 1.0, delta=0.01)
            self.assertAlmostEqual(ox_reset, 0.0, delta=0.01)
            self.assertAlmostEqual(oy_reset, 0.0, delta=0.01)

            canvas_element = page.query_selector("#concept-graph-canvas")
            box = canvas_element.bounding_box()
            cx = box["x"] + box["width"] / 2
            cy = box["y"] + box["height"] / 2

            # ponytail: dispatch mouse events directly on canvas to bypass headless hit-testing issues
            page.evaluate("""() => {
                const canvas = document.getElementById('concept-graph-canvas');
                const rect = canvas.getBoundingClientRect();
                const x1 = rect.left + 10, y1 = rect.top + 10;
                const x2 = rect.left + 110, y2 = rect.top + 60;
                canvas.dispatchEvent(new MouseEvent('mousedown', {clientX: x1, clientY: y1, bubbles: true}));
                canvas.dispatchEvent(new MouseEvent('mousemove', {clientX: x2, clientY: y2, bubbles: true}));
                canvas.dispatchEvent(new MouseEvent('mouseup', {bubbles: true}));
            }""")
            page.wait_for_timeout(500)

            ox_pan = page.evaluate("window.lastOffsetX")
            oy_pan = page.evaluate("window.lastOffsetY")
            self.assertGreater(abs(ox_pan), 20)
            self.assertGreater(abs(oy_pan), 10)

            page.click("button[title='Reset View']")
            page.wait_for_timeout(200)
            self.assertAlmostEqual(page.evaluate("window.lastZoomScale"), 1.0, delta=0.01)

            page.evaluate("""() => {
                const canvas = document.getElementById("concept-graph-canvas");
                const cx = canvas.width / 2;
                const cy = canvas.height / 2;
                window.capturedNodes[0].x = cx;
                window.capturedNodes[0].y = cy;
                window.capturedNodes[0].targetX = cx;
                window.capturedNodes[0].targetY = cy;
            }""")
            page.wait_for_timeout(200)

            first_node = page.evaluate("window.capturedNodes[0]")
            node_id = first_node["id"]

            coords_1 = page.evaluate("window.getNodeClickCoords(0, 10)")
            page.evaluate("window.selectedNodeId = null")
            page.mouse.click(coords_1["x"], coords_1["y"])
            page.wait_for_timeout(200)

            sel_id = page.evaluate("window.selectedNodeId")
            self.assertEqual(sel_id, node_id, f"Node not selected at 1.0x zoom! Expected {node_id}, got {sel_id}")

            coords_far = page.evaluate("window.getNodeClickCoords(0, 35)")
            page.evaluate("window.selectedNodeId = null")
            page.mouse.click(coords_far["x"], coords_far["y"])
            page.wait_for_timeout(200)
            sel_id_far = page.evaluate("window.selectedNodeId")
            self.assertIsNone(sel_id_far, f"Node should not be selected when clicking far away, got {sel_id_far}")

            page.evaluate("if (window.closePreview) window.closePreview();")
            page.click("button[title='Reset View']")
            page.evaluate("window.zoomConceptGraph(0.2)")
            page.wait_for_timeout(200)
            
            coords_02 = page.evaluate("window.getNodeClickCoords(0, 10)")
            page.evaluate("window.selectedNodeId = null")
            page.mouse.click(coords_02["x"], coords_02["y"])
            page.wait_for_timeout(200)
            
            sel_id_02 = page.evaluate("window.selectedNodeId")
            self.assertEqual(sel_id_02, node_id, f"Node not selected at 0.2x zoom! Expected {node_id}, got {sel_id_02}")

            page.evaluate("if (window.closePreview) window.closePreview();")

            page.click("button[title='Reset View']")
            page.evaluate("window.zoomConceptGraph(5.0)")
            page.wait_for_timeout(200)
            page.evaluate("""() => {
                const canvas = document.getElementById("concept-graph-canvas");
                const cx = canvas.width / 2;
                const cy = canvas.height / 2;
                window.capturedNodes[0].x = (cx - window.lastOffsetX) / window.lastZoomScale;
                window.capturedNodes[0].y = (cy - window.lastOffsetY) / window.lastZoomScale;
                window.capturedNodes[0].targetX = window.capturedNodes[0].x;
                window.capturedNodes[0].targetY = window.capturedNodes[0].y;
                window.capturedNodes[0].vx = 0;
                window.capturedNodes[0].vy = 0;
                if (typeof window.rebuildSpatialGrid === 'function') window.rebuildSpatialGrid();
                if (typeof window.setGraphNeedsRedraw === 'function') window.setGraphNeedsRedraw();
            }""")
            page.wait_for_timeout(200)
            
            coords_5 = page.evaluate("window.getNodeClickCoords(0, 10)")
            page.evaluate("window.selectedNodeId = null")
            page.mouse.click(coords_5["x"], coords_5["y"])
            page.wait_for_timeout(200)
            
            sel_id_5 = page.evaluate("window.selectedNodeId")
            self.assertEqual(sel_id_5, node_id, f"Node not selected at 5.0x zoom! Expected {node_id}, got {sel_id_5}")

            browser.close()


if __name__ == "__main__":
    unittest.main()
