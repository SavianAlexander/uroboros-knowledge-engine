import unittest
from src.domain.multimodal_ocr_parser import parse_multimodal_document_layout, parse_markdown_tables, extract_key_value_pairs, parse_checkbox_states
from src.domain.acl_permission_engine import is_user_authorized, trim_search_results_by_acl
from fastapi.testclient import TestClient
from src.app.main import app

class TestMultimodalAndAcl(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_01_parse_markdown_tables(self):
        md = "| Item | Qty | Price |\n|---|---|---|\n| Widget | 5 | $10.00 |\n| Gadget | 2 | $25.00 |"
        tables = parse_markdown_tables(md)
        self.assertEqual(len(tables), 1)
        self.assertEqual(tables[0]["row_count"], 2)

    def test_02_extract_key_value_pairs(self):
        text = "Invoice #: INV-9901\nTotal Amount: $1,250.00"
        kv = extract_key_value_pairs(text)
        self.assertEqual(kv.get("Invoice #"), "INV-9901")

    def test_03_parse_checkbox_states(self):
        text = "- [x] System Telemetry Audit\n- [ ] Multi-tenant Security Check"
        cb = parse_checkbox_states(text)
        self.assertEqual(len(cb["checked"]), 1)
        self.assertEqual(len(cb["unchecked"]), 1)

    def test_04_acl_permission_trimming(self):
        user_hr = {"user_id": 101, "roles": ["HR_Admin"], "clearance_level": 3}
        user_dev = {"user_id": 102, "roles": ["Developer"], "clearance_level": 1}

        doc_confidential = {"filename": "payroll.md", "acl": {"read_roles": ["HR_Admin"], "clearance_level": 3}}
        doc_public = {"filename": "readme.md", "acl": {"read_roles": ["*"], "clearance_level": 0}}

        self.assertTrue(is_user_authorized(user_hr, doc_confidential["acl"]))
        self.assertFalse(is_user_authorized(user_dev, doc_confidential["acl"]))

        trimmed_dev = trim_search_results_by_acl(user_dev, [doc_confidential, doc_public])
        self.assertEqual(len(trimmed_dev), 1)
        self.assertEqual(trimmed_dev[0]["filename"], "readme.md")

    def test_05_multimodal_and_acl_endpoints(self):
        res1 = self.client.post("/api/file/parse-multimodal", json={"text": "Invoice #: 12345"})
        self.assertEqual(res1.status_code, 200)
        self.assertEqual(res1.json()["status"], "success")

        res2 = self.client.post("/api/search/acl-trimmed-search", json={
            "user_context": {"roles": ["Dev"]},
            "results": [{"filename": "public.md", "read_roles": ["Dev"]}]
        })
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res2.json()["status"], "success")

if __name__ == "__main__":
    unittest.main()
