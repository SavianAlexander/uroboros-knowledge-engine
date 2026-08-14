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
        self.assertIn("gzip_static on;", content)
        self.assertIn("location /assets/", content)
        self.assertIn("max-age=31536000, immutable", content)
        self.assertIn("limit_req_zone", content)
        self.assertIn("limit_req status 429;" if "limit_req status" in content else "limit_req_status 429;", content)

    def test_docker_compose_structure(self):
        dc_path = BASE_DIR / "docker-compose.yml"
        self.assertTrue(dc_path.exists())
        content = dc_path.read_text(encoding="utf-8")
        self.assertIn("service_healthy", content)
        self.assertIn("limits:", content)
        self.assertIn("max-size:", content)
        self.assertIn("develop:", content)
        self.assertIn("watch:", content)
        self.assertIn("tmpfs:", content)
        self.assertIn("taskmaster_bridge", content)

    def test_dockerignore_coverage(self):
        di_path = BASE_DIR / ".dockerignore"
        self.assertTrue(di_path.exists())
        content = di_path.read_text(encoding="utf-8")
        self.assertIn(".coverage", content)
        self.assertIn("*.db", content)

    def test_docker_clean_script_exists(self):
        script_path = BASE_DIR / "scripts" / "docker_clean.ps1"
        self.assertTrue(script_path.exists())
        content = script_path.read_text(encoding="utf-8")
        self.assertIn("docker builder prune", content)

    def test_env_example_ports(self):
        env_path = BASE_DIR / ".env.example"
        self.assertTrue(env_path.exists())
        content = env_path.read_text(encoding="utf-8")
        self.assertIn("ENGINE_HOST_PORT", content)
        self.assertIn("FRONTEND_HOST_PORT", content)

    def test_github_actions_frontend_container(self):
        wf_path = BASE_DIR / ".github" / "workflows" / "build.yml"
        self.assertTrue(wf_path.exists())
        content = wf_path.read_text(encoding="utf-8")
        self.assertIn("Dockerfile.frontend", content)
        self.assertIn("meta-frontend", content)
        self.assertIn("platforms: linux/amd64,linux/arm64", content)
        self.assertIn("setup-qemu-action", content)

    def test_frontend_compress_script(self):
        comp_path = BASE_DIR / "frontend" / "compress.mjs"
        self.assertTrue(comp_path.exists())
        content = comp_path.read_text(encoding="utf-8")
        self.assertIn("gzipSync", content)
        self.assertIn("Z_BEST_COMPRESSION", content)

    def test_tune_wsl_script(self):
        wsl_script = BASE_DIR / "scripts" / "tune_wsl.ps1"
        self.assertTrue(wsl_script.exists())
        content = wsl_script.read_text(encoding="utf-8")
        self.assertIn(".wslconfig", content)
        self.assertIn("memory=6GB", content)

if __name__ == "__main__":
    unittest.main()
