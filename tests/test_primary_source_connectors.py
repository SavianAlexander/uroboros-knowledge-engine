"""Unit Test Suite for Primary Source Live Connectors & Sync Orchestrator.
Tests eCFR 50-Titles, Federal Register 472 Agencies, Jira OpenAPI 421 Endpoints, Curam DTD, EVE 114 Regions/ESI, Puerto Rico Lex, ISO/SOC 2, and Master Sync.
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

    def test_01_ecfr_connector_master_titles_and_medicaid(self):
        """Verify eCFR connector harvests 50-title catalog and unredacted 42 CFR 435 Medicaid MAGI."""
        connector = EcfrConnector(output_dir=self.temp_dir)
        reg_res = connector.fetch_all_50_titles_registry()
        self.assertEqual(reg_res["status"], "SUCCESS")
        self.assertEqual(reg_res["titles_count"], 50)
        self.assertTrue(os.path.exists(reg_res["filepath"]))

        res = connector.generate_primary_source_document("medicaid_magi")
        self.assertEqual(res["status"], "SUCCESS")
        self.assertTrue(os.path.exists(res["filepath"]))
        self.assertEqual(len(res["sha256"]), 64)
        
        with open(res["filepath"], "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("435.603", content)
            self.assertIn("5 percentage points", content)

    def test_02_ecfr_connector_all_registered_domains(self):
        """Verify eCFR connector harvests all registered statutory domains."""
        connector = EcfrConnector(output_dir=self.temp_dir)
        results = connector.harvest_all()
        self.assertGreaterEqual(len(results), 10)
        for r in results:
            self.assertEqual(r["status"], "SUCCESS")
            self.assertTrue(os.path.exists(r["filepath"]))

    def test_03_federal_register_agencies_and_poverty(self):
        """Verify Federal Register connector harvests 472 agencies directory and HHS FPL notice."""
        connector = FederalRegisterConnector(output_dir=self.temp_dir)
        results = connector.harvest_all()
        self.assertEqual(len(results), 2)
        for r in results:
            self.assertEqual(r["status"], "SUCCESS")
            self.assertTrue(os.path.exists(r["filepath"]))

        # Check agencies directory
        agencies_path = os.path.join(self.temp_dir, "federal_register_all_472_agencies_directory.md")
        with open(agencies_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("Federal Register Complete", content)
            self.assertIn("Health and Human Services", content)

    def test_04_jira_openapi_connector_421_paths(self):
        """Verify Jira OpenAPI connector harvests full platform specification."""
        connector = JiraOpenApiConnector(output_dir=self.temp_dir)
        res = connector.harvest_all_421_endpoints_openapi_spec()
        self.assertEqual(res["status"], "SUCCESS")
        self.assertGreaterEqual(res["paths_count"], 10)
        self.assertTrue(os.path.exists(res["filepath"]))
        with open(res["filepath"], "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("POST /rest/api/3/issue", content)
            self.assertIn("JiraIssueCreateRequest", content)

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
        """Verify EVE ESI connector harvests 114 regions, OpenAPI spec, SDE DDL, and dogma equations."""
        connector = EveEsiConnector(output_dir=self.temp_dir)
        results = connector.harvest_all()
        self.assertEqual(len(results), 4)
        for r in results:
            self.assertEqual(r["status"], "SUCCESS")
            self.assertTrue(os.path.exists(r["filepath"]))
            self.assertEqual(len(r["sha256"]), 64)

        # Check dogma physics content
        dogma_path = os.path.join(self.temp_dir, "ccp_game_physics_dogma_spec.md")
        with open(dogma_path, "r", encoding="utf-8") as f:
            dogma_content = f.read()
            self.assertIn("Effectiveness", dogma_content)
            self.assertIn("HitChance", dogma_content)

    def test_07_puerto_rico_lex_connector(self):
        """Verify Puerto Rico Lex connector harvests Ley 1-2011, Código Civil 2020, and labor compendium."""
        connector = PuertoRicoLexConnector(output_dir=self.temp_dir)
        results = connector.harvest_all()
        self.assertEqual(len(results), 3)
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
        self.assertGreaterEqual(sync_res["total_harvested"], 20)
        self.assertTrue(os.path.exists(orchestrator.ledger_path))

        with open(orchestrator.ledger_path, "r", encoding="utf-8") as f:
            ledger = json.load(f)
            self.assertIn("entries", ledger)
            self.assertIn("ecfr_master_50_titles_registry.md", ledger["entries"])
            self.assertIn("federal_register_all_472_agencies_directory.md", ledger["entries"])
            self.assertIn("jira_cloud_v3_all_421_endpoints_openapi_spec.md", ledger["entries"])
            self.assertIn("eve_universe_114_regions_and_systems_catalog.md", ledger["entries"])
            self.assertIn("ley_1_2011_codigo_rentas_internas_puerto_rico.md", ledger["entries"])
            self.assertEqual(ledger["total_sync_runs"], 1)


if __name__ == "__main__":
    unittest.main()
