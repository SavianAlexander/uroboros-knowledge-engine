import os
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class TestDockerConfig(unittest.TestCase):
    def test_dockerfile_multi_stage(self):
        df_path = BASE_DIR / "Dockerfile"
        self.assertTrue(df_path.exists())
        content = df_path.read_text(encoding="utf-8")
        self.assertTrue("AS builder" in content or "AS python-builder" in content)
        self.assertIn("FROM python:3.12-slim AS runner", content)
        self.assertIn("HEALTHCHECK", content)

    def test_nginx_conf_sse(self):
        nginx_path = BASE_DIR / "nginx.conf"
        self.assertTrue(nginx_path.exists())
        content = nginx_path.read_text(encoding="utf-8")
        self.assertIn("proxy_buffering off;", content)
        self.assertIn("gzip on;", content)

    def test_docker_compose_structure(self):
        dc_path = BASE_DIR / "docker-compose.yml"
        self.assertTrue(dc_path.exists())
        content = dc_path.read_text(encoding="utf-8")
        self.assertIn("service_healthy", content)
        self.assertIn("limits:", content)
        self.assertIn("max-size:", content)

if __name__ == "__main__":
    unittest.main()
