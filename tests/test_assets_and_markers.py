import os
import re
import unittest
import xml.etree.ElementTree as ET

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class TestAssetsAndMarkers(unittest.TestCase):
    """Domain test verifying static asset integrity and SVG validity."""

    def test_svg_assets_valid_xml(self):
        """Check that all SVG files in assets/ directory are valid XML."""
        assets_dir = os.path.join(PROJECT_ROOT, "assets")
        invalid_svgs = []
        for root, _, filenames in os.walk(assets_dir):
            for fname in filenames:
                if fname.endswith(".svg"):
                    full_p = os.path.join(root, fname)
                    try:
                        ET.parse(full_p)
                    except ET.ParseError as e:
                        invalid_svgs.append((fname, str(e)))

        self.assertEqual(invalid_svgs, [], f"Invalid SVG files detected: {invalid_svgs}")

    def test_assets_static_endpoint_serves_files(self):
        """Check that mounted /assets endpoint serves static SVG files without HTTP 404 errors."""
        import main
        from fastapi.testclient import TestClient
        client = TestClient(main.app)
        response = client.get("/assets/brand_logo.svg")
        self.assertEqual(response.status_code, 200, "Mounted /assets endpoint returned non-200 status for brand_logo.svg")
        self.assertIn("<svg", response.text.lower())

    def test_html_title_and_favicon_marker(self):
        """Check that index.html specifies title and favicon asset link."""
        index_path = os.path.join(PROJECT_ROOT, "index.html")
        with open(index_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        self.assertIn("<title>Uroboros Knowledge Engine</title>", html_content)
        self.assertIn('href="/assets/favicon.svg"', html_content)


if __name__ == "__main__":
    unittest.main()
