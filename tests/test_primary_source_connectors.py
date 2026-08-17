"""Unit Test Suite for Primary Source Live Connectors & Sync Orchestrator.
Tests eCFR, Federal Register, Jira OpenAPI, Curam DTD, EVE ESI, Puerto Rico Lex, ISO/SOC 2, and Master Sync.
"""

import unittest
import os
import tempfile
import json
import shutil

from src.domain.connectors.ecfr_connector import EcfrConnector
from src.domain.connectors.federal_register_connector import FederalRegisterConnector
from src.domain.connectors.jira_openapi_connector import JiraOpenApiConnector
from src.domain.connectors.curam_spec_connector import CuramSpecConnector
from src.domain.connectors.eve_esi_connector import EveEsiConnector
from src.domain.connectors.puerto_rico_lex_connector import PuertoRicoLexConnector
from src.domain.connectors.uat_iso_connector import UatIsoConnector
from src.domain.sync_orchestrator import PrimarySourceSyncOrchestrator


class TestPrimarySourceConnectors(unittest.TestCase):
    """Test suite for unabridged primary source harvesting and synchronization."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_ecfr_connector_medicaid_magi(self):
        """Verify eCFR connector harvests unredacted 42 CFR 435 Medicaid MAGI."""
        connector = EcfrConnector(output_dir=self.temp_dir)
        res = connector.generate_primary_source_document("medicaid_magi")
        self.assertEqual(res["status"], "SUCCESS")
        self.assertTrue(os.path.exists(res["filepath"]))
        self.assertEqual(len(res["sha256"]), 64)
        
        with open(res["filepath"], "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("435.603", content)
            self.assertIn("5 percentage points", content)
            self.assertIn("No resource or asset test", content)

    def test_02_ecfr_connector_snap_nutrition(self):
        """Verify eCFR connector harvests unredacted 7 CFR 273 SNAP regulations."""
        connector = EcfrConnector(output_dir=self.temp_dir)
        res = connector.generate_primary_source_document("snap_nutrition")
        self.assertEqual(res["status"], "SUCCESS")
        with open(res["filepath"], "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("130 percent", content)
            self.assertIn("Twenty percent (20%)", content)
            self.assertIn("Excess shelter deduction", content)

    def test_03_federal_register_poverty_guidelines(self):
        """Verify Federal Register connector harvests official HHS FPL notice."""
        connector = FederalRegisterConnector(output_dir=self.temp_dir)
        res = connector.harvest_annual_poverty_guidelines(2026)
        self.assertEqual(res["status"], "SUCCESS")
        with open(res["filepath"], "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("$15,650.00", content)
            self.assertIn("138% Medicaid Expansion", content)
            self.assertIn("Alaska (125% Statutory Adjustment)", content)

    def test_04_jira_openapi_connector(self):
        """Verify Jira OpenAPI connector harvests valid OpenAPI 3.0 schema."""
        connector = JiraOpenApiConnector(output_dir=self.temp_dir)
        res = connector.harvest_jira_cloud_openapi_spec()
        self.assertEqual(res["status"], "SUCCESS")
        with open(res["filepath"], "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("POST /rest/api/3/issue", content)
            self.assertIn("XrayTestStepSpecification", content)

    def test_05_curam_spec_connector(self):
        """Verify Curam Spec connector harvests official CER XML DTD."""
        connector = CuramSpecConnector(output_dir=self.temp_dir)
        res = connector.harvest_cer_xml_dtd_specification()
        self.assertEqual(res["status"], "SUCCESS")
        with open(res["filepath"], "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("<!ELEMENT RuleSet (Class*)>", content)
            self.assertIn("<RuleSet name=\"MedicaidMAGIEligibilityRuleSet\">", content)

    def test_06_eve_esi_connector(self):
        """Verify EVE ESI connector harvests OpenAPI spec, SDE DDL, and dogma equations."""
        connector = EveEsiConnector(output_dir=self.temp_dir)
        results = connector.harvest_all()
        self.assertEqual(len(results), 3)
        for r in results:
            self.assertEqual(r["status"], "SUCCESS")
            self.assertTrue(os.path.exists(r["filepath"]))
            self.assertEqual(len(r["sha256"]), 64)

        # Check dogma physics content
        dogma_path = os.path.join(self.temp_dir, "ccp_game_physics_dogma_spec.md")
        with open(dogma_path, "r", encoding="utf-8") as f:
            dogma_content = f.read()
            self.assertIn("S(n) = e^{-(n-1)^2 / 7.1289}", dogma_content)
            self.assertIn("Chance to Hit", dogma_content)

    def test_07_puerto_rico_lex_connector(self):
        """Verify Puerto Rico Lex connector harvests Ley 1-2011 and Ley 4-2017."""
        connector = PuertoRicoLexConnector(output_dir=self.temp_dir)
        results = connector.harvest_all()
        self.assertEqual(len(results), 2)
        for r in results:
            self.assertEqual(r["status"], "SUCCESS")
            self.assertTrue(os.path.exists(r["filepath"]))

        # Check SUT / IVU rates
        rentas_path = os.path.join(self.temp_dir, "ley_1_2011_codigo_rentas_internas_puerto_rico.md")
        with open(rentas_path, "r", encoding="utf-8") as f:
            rentas_content = f.read()
            self.assertIn("diez punto cinco por ciento (10.5%)", rentas_content)
            self.assertIn("once punto cinco por ciento (11.5%)", rentas_content)

    def test_08_uat_iso_connector(self):
        """Verify UAT ISO connector harvests ISO 29119 and SOC 2 criteria."""
        connector = UatIsoConnector(output_dir=self.temp_dir)
        results = connector.harvest_all()
        self.assertEqual(len(results), 2)
        for r in results:
            self.assertEqual(r["status"], "SUCCESS")
            self.assertTrue(os.path.exists(r["filepath"]))

        soc2_path = os.path.join(self.temp_dir, "aicpa_soc2_type2_trust_services_criteria.md")
        with open(soc2_path, "r", encoding="utf-8") as f:
            soc2_content = f.read()
            self.assertIn("CC6.8 - Cryptographic Hash Verification", soc2_content)
            self.assertIn("PI1.1 - Processing Input Validation", soc2_content)

    def test_09_sync_orchestrator_ledger_persistence(self):
        """Verify SyncOrchestrator tracks hashes and records persistent sync ledger for all domains."""
        orchestrator = PrimarySourceSyncOrchestrator(vault_root=self.temp_dir)
        sync_res = orchestrator.execute_sync(auto_index=False)
        self.assertEqual(sync_res["status"], "SUCCESS")
        self.assertEqual(sync_res["total_harvested"], 16)
        self.assertTrue(os.path.exists(orchestrator.ledger_path))

        with open(orchestrator.ledger_path, "r", encoding="utf-8") as f:
            ledger = json.load(f)
            self.assertIn("entries", ledger)
            self.assertIn("ecfr_title42_part435_medicaid_magi.md", ledger["entries"])
            self.assertIn("eve_esi_v2_openapi_spec.md", ledger["entries"])
            self.assertIn("ley_1_2011_codigo_rentas_internas_puerto_rico.md", ledger["entries"])
            self.assertIn("iso_ieee_29119_test_documentation_spec.md", ledger["entries"])
            self.assertEqual(ledger["total_sync_runs"], 1)


if __name__ == "__main__":
    unittest.main()
