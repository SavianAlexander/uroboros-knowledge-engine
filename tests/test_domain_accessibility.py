import os
import sys
import unittest
import xml.etree.ElementTree as ET
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
        """Verify WCAG 1.1.1: Every <img> tag MUST have an alt attribute or aria-hidden status.

        Preconditions: index.html parsed via HTMLAccessibilityParser.
        Invariants: All img elements contain non-null alt attribute keys.
        Expected Outcomes: List of images missing alt attribute is empty (len == 0).
        """
        self.assertEqual(
            len(self.parser.images_without_alt), 0,
            f"Images missing alt attribute detected: {self.parser.images_without_alt}"
        )

    def test_02_all_inputs_have_accessible_identifiers(self):
        """Verify WCAG 1.3.1 / 4.1.2: Form inputs MUST have accessible labels, IDs, or placeholders.

        Preconditions: index.html parsed via HTMLAccessibilityParser.
        Invariants: All input elements provide id, aria-label, or placeholder attribute for screen readers.
        Expected Outcomes: List of inputs missing accessible labels is empty (len == 0).
        """
        self.assertEqual(
            len(self.parser.inputs_without_labels), 0,
            f"Inputs missing accessible labels detected: {self.parser.inputs_without_labels}"
        )

    def test_03_heading_hierarchy_single_h1(self):
        """Verify WCAG 1.3.1: Document MUST contain exactly one top-level <h1> heading.

        Preconditions: Document heading tags extracted from index.html during parsing.
        Invariants: Root HTML document structure has single primary heading element.
        Expected Outcomes: Count of 'h1' tags in heading list equals 1.
        """
        h1_count = self.parser.headings.count("h1")
        self.assertEqual(h1_count, 1, f"Expected exactly 1 <h1> heading, found {h1_count}")

    def test_04_html_lang_attribute_present(self):
        """Verify WCAG 3.1.1: Document root <html> tag MUST specify a valid lang attribute.

        Preconditions: index.html raw file content read into memory string.
        Invariants: HTML root element declares primary language identifier.
        Expected Outcomes: String content contains '<html lang="en">'.
        """
        self.assertIn('<html lang="en">', self.html_content.lower())

    def test_05_meta_viewport_user_scalable_safety(self):
        """Verify WCAG 1.4.4: Meta viewport MUST NOT disable user zoom scaling.

        Preconditions: index.html raw file content loaded.
        Invariants: Viewport meta tag preserves accessibility zoom scaling capabilities.
        Expected Outcomes: Document text does not contain 'user-scalable=no' or 'maximum-scale=1'.
        """
        self.assertNotIn("user-scalable=no", self.html_content.lower())
        self.assertNotIn("maximum-scale=1", self.html_content.lower())

if __name__ == "__main__":
    unittest.main()
