"""
Final Gate Stress Verification Test Suite for AI Debate Auditor & Counter-Argument Engine.
Authored by Final Adversarial Verification (Iteration 2 Gate Stress Verification).
"""

import unittest
import time
import json
import re
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tools.ai_debate_auditor.engine import DebateAuditorEngine, audit_text
from tools.ai_debate_auditor.models import (
    AuditReport,
    ClaimCategory,
    PatternSeverity,
    PatternType,
    CitationStatus,
    EpistemicVerdict
)
from tools.ai_debate_auditor.verifier import (
    extract_citations,
    cross_examine_vault,
    verify_boundaries,
    SPEED_OF_LIGHT,
    BOLTZMANN_K,
    LANDAUER_ROOM_TEMP_J
)
from tools.ai_debate_auditor.patterns import (
    run_full_pattern_scan,
    detect_p01_sycophancy,
    detect_p02_confirmation_bias,
    detect_p05_false_dilemma,
    detect_p06_circular_logic,
    detect_p07_quantifier_inflation,
    detect_p08_premise_contradiction,
    detect_p09_spurious_causation,
    detect_p10_reification
)
from tools.ai_debate_auditor.synthesizer import (
    synthesize_counter_arguments,
    synthesize_first_principles_counter_proofs
)
from tools.ai_debate_auditor.reporter import compute_scoring_metrics, render_markdown_report


class TestFinalVerificationAdversarialGate(unittest.TestCase):
    """Exhaustive Empirical Stress Verification Suite for Iteration 2 Gate."""

    def setUp(self):
        self.engine = DebateAuditorEngine()

    # =========================================================================
    # 1. 100k+ Character Payloads & ReDoS Resistance (< 0.5s execution)
    # =========================================================================

    def test_redos_monolithic_character_streams(self):
        """Verify that 100k+ monolithic strings execute without catastrophic backtracking in < 0.5s."""
        payloads = [
            ("Monolithic 100k 'A' stream", "A" * 100_000),
            ("Repeated pseudo-author tokens without comma 100k", ("Smith " * 16_000)[:100_000]),
            ("Repeated punctuation and quotes 100k", (r"(\"test\" [123] 10.9999/x.y) " * 4_000)[:100_000]),
            ("Alternating title words 100k", ("Theoretical Journal of Quantum " * 3_500)[:100_000]),
        ]

        for label, payload in payloads:
            t0 = time.perf_counter()
            cites = extract_citations(payload)
            elapsed_cites = time.perf_counter() - t0
            self.assertLess(
                elapsed_cites, 0.85,
                f"ReDoS bottleneck detected in extract_citations for '{label}': took {elapsed_cites:.4f}s (budget: <0.85s)"
            )

            t1 = time.perf_counter()
            violations = verify_boundaries(payload)
            elapsed_bounds = time.perf_counter() - t1
            self.assertLess(
                elapsed_bounds, 0.50,
                f"ReDoS bottleneck detected in verify_boundaries for '{label}': took {elapsed_bounds:.4f}s (budget: <0.50s)"
            )

    # =========================================================================
    # 2. Valid Academic DOIs (Zero NameError / Unhandled Exception)
    # =========================================================================

    def test_valid_academic_dois_zero_exceptions(self):
        """Verify valid DOIs from CrossRef, Nature, APS, IEEE, Cell do NOT trigger NameError or false phantom flags."""
        valid_dois = [
            "doi:10.1000/182",
            "doi:10.1038/nature12373",
            "doi:10.1103/PhysRevLett.116.061102",
            "doi:10.1016/j.cell.2020.08.010",
            "doi:10.1109/TIT.1948.1057465",
            "10.1073/pnas.1912345116",
            "10.1145/3372297.3417234",
            "10.1007/s11276-021-02685-z",
        ]

        for doi in valid_dois:
            text = f"As rigorously proven by foundational research in {doi}, the mechanism is robust."
            try:
                report = self.engine.audit_text(text)
            except NameError as ne:
                self.fail(f"NameError raised on valid DOI '{doi}': {ne}")
            except Exception as exc:
                self.fail(f"Unhandled exception raised on valid DOI '{doi}': {exc}")

            self.assertEqual(len(report.citations), 1, f"DOI '{doi}' was not extracted!")
            cite = report.citations[0]
            self.assertTrue(cite.is_valid, f"Valid DOI '{doi}' marked as invalid!")
            self.assertFalse(cite.is_phantom, f"Valid DOI '{doi}' falsely marked as phantom!")
            self.assertNotEqual(cite.status, CitationStatus.PHANTOM_FABRICATED)
            self.assertIn(report.verdict, [EpistemicVerdict.SOUND, EpistemicVerdict.QUESTIONABLE])

    # =========================================================================
    # 3. 0W Input Power Claims (ZeroDivisionError Guard & First Law Violation)
    # =========================================================================

    def test_zero_watt_input_power_claims(self):
        """Verify zero division safety and correct First Law violation on 0W input power assertions."""
        zero_watt_claims = [
            ("The engine produces 100W from 0W input.", "100.0 w", "0.0 w"),
            ("Produces 5 kW of electrical output from 0 kW input.", "5.0 kw", "0.0 kw"),
            ("Generates 10 MW with 0 W input continuously.", "10.0 mw", "0.0 w"),
            ("Output of 2500 Watts from 0 Watts input.", "2500.0 watts", "0.0 watts"),
            ("Yields 1 GW from 0 GW input ex nihilo.", "1.0 gw", "0.0 gw"),
        ]

        for claim, expected_out, expected_in in zero_watt_claims:
            try:
                violations = verify_boundaries(claim)
            except ZeroDivisionError as zde:
                self.fail(f"ZeroDivisionError raised on 0W input power claim '{claim}': {zde}")
            except Exception as exc:
                self.fail(f"Unhandled exception on 0W input power claim '{claim}': {exc}")

            self.assertGreaterEqual(len(violations), 1, f"0W free energy claim '{claim}' was not flagged!")
            thermo_viol = [v for v in violations if "First Law" in v.law_name or v.domain == "Thermodynamics"]
            self.assertTrue(len(thermo_viol) >= 1)
            v = thermo_viol[0]
            self.assertIn("Infinite %", v.claimed_value)
            self.assertEqual(v.theoretical_limit, "Output <= Input (eta <= 100%)")

            # End-to-end report check
            report = self.engine.audit_text(claim)
            self.assertEqual(report.verdict, EpistemicVerdict.DEBUNKED)
            self.assertGreaterEqual(report.metrics.hallucination_risk_score, 0.85)

    # =========================================================================
    # 4. Percentage Figures Ending in Punctuation ("1500%.", "120%!", "80%?")
    # =========================================================================

    def test_percentages_ending_in_punctuation(self):
        """Verify boundary checks on percentages ending in '.', '!', '?', ',', ';', ':', ')', ']'."""
        test_cases = [
            ("Our motor achieves 1500%.", "First Law"),
            ("The device reaches 1200%!", "First Law"),
            ("Does the prototype output 800%?", "First Law"),
            ("With an efficiency of 250%, the prototype operates.", "First Law"),
            ("The engine achieved 350%; power was monitored.", "First Law"),
            ("With electrical efficiency of 450%:", "First Law"),
            ("The calculated probability of success is 120%!", "Kolmogorov"),
            ("Is the event probability 150%?", "Kolmogorov"),
            ("Probability of failure was 130%.", "Kolmogorov"),
            ("Can a wind turbine extract 80%?", "Betz"),
            ("Wind turbine achieves 75%.", "Betz"),
            ("Wind turbine captures 90%!", "Betz"),
        ]

        for text, expected_law in test_cases:
            violations = verify_boundaries(text)
            matching = [v for v in violations if expected_law in v.law_name]
            self.assertGreaterEqual(
                len(matching), 1,
                f"Failed to detect {expected_law} violation on punctuated percentage: '{text}'"
            )

    # =========================================================================
    # 5. Sound Combined-Cycle Turbines (Zero Carnot False Positives)
    # =========================================================================

    def test_sound_combined_cycle_turbines_zero_false_positives(self):
        """Verify that multi-sentence and intra-sentence combined cycle texts do NOT trigger Carnot false positives."""
        sound_scenarios = [
            # Standard combined-cycle with subsequent sentence energy recovery
            "A combined cycle gas turbine operating between 300 K and 1400 K achieves 58% thermal efficiency. "
            "The system operates with 85% energy recovery.",

            # Semicolon-separated statements
            "The engine operating between 300 K and 1200 K achieves 50% thermal efficiency; "
            "the bottoming cycle provides 70% overall heat recovery.",

            # Valid high-efficiency turbine well within Carnot limit (Carnot limit at 300K/1500K is 80.0%)
            "Operating between 300 K and 1500 K with an electrical efficiency of 62% in combined-cycle mode.",

            # Paragraph with unrelated percentages in surrounding sentences
            "Our facility installed an advanced turbine. The cycle operating between 350 K and 1100 K yields 48% efficiency. "
            "Staff satisfaction increased by 95%. Compliance reached 99% across all audits.",
        ]

        for scenario in sound_scenarios:
            violations = verify_boundaries(scenario)
            carnot_violations = [v for v in violations if "Carnot" in v.law_name]
            self.assertEqual(
                len(carnot_violations), 0,
                f"Carnot false positive on sound combined-cycle text: '{scenario}'"
            )

        # Negative control: verify that genuinely impossible Carnot claim IS detected
        # T_cold=300K, T_hot=600K -> Carnot limit is 50.0%. Claim: 65% -> Violation
        bad_scenario = "A heat engine operating between 300 K and 600 K achieves 65% thermal efficiency."
        bad_violations = verify_boundaries(bad_scenario)
        bad_carnot = [v for v in bad_violations if "Carnot" in v.law_name]
        self.assertEqual(len(bad_carnot), 1, "Failed to flag genuinely impossible Carnot efficiency!")

    # =========================================================================
    # 6. Multi-Word Kolmogorov Events & Scalar Decimal Probabilities
    # =========================================================================

    def test_multi_word_kolmogorov_events_and_scalar_decimals(self):
        """Verify detection of multi-word event descriptors and scalar decimal probabilities P > 1.0 or P < 0."""
        cases = [
            ("The calculated probability of market growth is 125% next year.", "Probability Theory"),
            ("The probability of unexpected catastrophic core failure is 180%.", "Probability Theory"),
            ("The probability of severe algorithmic model collapse equals 250%.", "Probability Theory"),
            ("The calculated probability is 1.5 in our predictive model.", "Probability Theory"),
            ("The estimated probability is 2.75 under stress conditions.", "Probability Theory"),
            ("In our analysis, probability = 3.2.", "Probability Theory"),
            ("The probability of event completion is -0.25 due to calculation error.", "Probability Theory"),
            ("Calculated p = -1.5.", "Probability Theory"),
        ]

        for text, expected_domain in cases:
            violations = verify_boundaries(text)
            matching = [v for v in violations if v.domain == expected_domain]
            self.assertGreaterEqual(
                len(matching), 1,
                f"Failed to detect Kolmogorov violation in: '{text}'"
            )

    # =========================================================================
    # 7. Landauer Bound Bit Erasure Claims
    # =========================================================================

    def test_landauer_bound_bit_erasure_verifications(self):
        """Verify Landauer principle enforcement on zero-dissipation bit erasure claims."""
        landauer_claims = [
            "Our quantum computer achieved irreversible bit erasure with zero energy dissipation.",
            "The memory module executes irreversible bit erasure without any energy dissipation.",
            "Demonstrated zero-dissipation irreversible bit erasure at room temperature.",
            "Achieved sub-landauer energy dissipation during logical state reset operations.",
            "The chip performs memory erasure with zero heat generation.",
        ]

        for claim in landauer_claims:
            violations = verify_boundaries(claim)
            landauer_v = [v for v in violations if "Landauer" in v.law_name]
            self.assertGreaterEqual(len(landauer_v), 1, f"Failed to flag Landauer violation on claim: '{claim}'")
            v = landauer_v[0]
            self.assertEqual(v.domain, "Information Theory")
            self.assertIn("k_B", v.theoretical_limit)

            # Test counter-proof synthesis
            proofs = synthesize_first_principles_counter_proofs(violations, [])
            self.assertGreaterEqual(len(proofs), 1)
            lp = proofs[0]
            self.assertIn("Landauer", lp.empirical_axiom)
            self.assertIn("k_B \\ln 2", lp.mathematical_derivation)
            self.assertTrue(any("Landauer, R. (1961)" in c for c in lp.primary_citations))

            # Full audit report check
            report = self.engine.audit_text(claim)
            self.assertEqual(report.verdict, EpistemicVerdict.DEBUNKED)

    # =========================================================================
    # 8. Special Relativity Relativistic Invariants
    # =========================================================================

    def test_special_relativity_invariants(self):
        """Verify Special Relativity enforcement across passive, transitive, and information propagation claims."""
        relativity_claims = [
            "The tachyonic signals were recorded propagating at 350000 km/s.",
            "Our optical transmitter transmits monitoring data at 500000 km/s.",
            "The information was observed traveling at 450,000 km/s.",
            "The particles were measured moving at 1.5 times the speed of light.",
            "The propagation speed of 350,000 km/s was confirmed in tests.",
        ]

        for claim in relativity_claims:
            violations = verify_boundaries(claim)
            rel_v = [v for v in violations if v.domain == "Special Relativity"]
            self.assertGreaterEqual(len(rel_v), 1, f"Failed to detect Special Relativity violation in: '{claim}'")
            report = self.engine.audit_text(claim)
            self.assertEqual(report.verdict, EpistemicVerdict.DEBUNKED)


if __name__ == "__main__":
    unittest.main()
