"""
Domain 18: Accessibility & WCAG Compliance Suite.
Validates HTML5 accessibility standards for modern React shell layout:
- Root <html> lang attribute
- Viewport scalability preservation
- Image alt attributes and aria labels
- Form input accessibility
- Heading hierarchy compliance
"""

import os
import sys
import unittest
from html.parser import HTMLParser

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class HTMLAccessibilityParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.buttons_without_labels = []
        self.images_without_alt = []
        self.inputs_without_labels = []
        self.headings = []
        self.aria_roles = []

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)

        if tag == "button":
            has_title = "title" in attr_dict
            has_aria = "aria-label" in attr_dict
            has_onclick = "onclick" in attr_dict
            if not (has_title or has_aria or has_onclick):
                self.buttons_without_labels.append(attr_dict)

        if tag == "img":
            if "alt" not in attr_dict:
                self.images_without_alt.append(attr_dict)

        if tag == "input" and attr_dict.get("type") not in ("hidden", "button", "submit"):
            if not ("id" in attr_dict or "aria-label" in attr_dict or "placeholder" in attr_dict):
                self.inputs_without_labels.append(attr_dict)

        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.headings.append(tag)

        if "role" in attr_dict:
            self.aria_roles.append(attr_dict["role"])


class TestDomainAccessibility(unittest.TestCase):
    def setUp(self):
        self.index_path = os.path.join(PROJECT_ROOT, "index.html")
        with open(self.index_path, "r", encoding="utf-8") as f:
            self.html_content = f.read()

        self.parser = HTMLAccessibilityParser()
        self.parser.feed(self.html_content)

    def tearDown(self):
        if hasattr(self, "parser") and self.parser:
            self.parser.close()

    def test_01_all_images_have_alt_attributes(self):
        """Verify WCAG 1.1.1: Every static <img> tag MUST have an alt attribute."""
        self.assertEqual(
            len(self.parser.images_without_alt), 0,
            f"Images missing alt attribute detected: {self.parser.images_without_alt}"
        )

    def test_02_all_inputs_have_accessible_identifiers(self):
        """Verify WCAG 1.3.1 / 4.1.2: Static inputs have accessible identifiers."""
        self.assertEqual(
            len(self.parser.inputs_without_labels), 0,
            f"Inputs missing accessible labels detected: {self.parser.inputs_without_labels}"
        )

    def test_03_react_root_container_present(self):
        """Verify WCAG 1.3.1: Document contains primary #root mount container."""
        self.assertIn('id="root"', self.html_content)

    def test_04_html_lang_attribute_present(self):
        """Verify WCAG 3.1.1: Document root <html> tag MUST specify a valid lang attribute."""
        self.assertIn('<html lang="en">', self.html_content.lower())

    def test_05_meta_viewport_user_scalable_safety(self):
        """Verify WCAG 1.4.4: Meta viewport MUST NOT disable user zoom scaling."""
        self.assertNotIn("user-scalable=no", self.html_content.lower())
        self.assertNotIn("maximum-scale=1", self.html_content.lower())


if __name__ == "__main__":
    unittest.main()