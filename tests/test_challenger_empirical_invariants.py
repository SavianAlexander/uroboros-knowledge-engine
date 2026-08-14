"""
Reproducible Empirical Physics & Mathematical Invariant Test Suite
Authored by Challenger 2 (Empirical & Mathematical Invariants)
"""

import unittest
from tools.ai_debate_auditor.verifier import (
    verify_boundaries,
    SPEED_OF_LIGHT,
    ABSOLUTE_ZERO_C
)
from tools.ai_debate_auditor.synthesizer import (
    synthesize_first_principles_counter_proofs,
    PRIMARY_FOUNDATIONAL_CITATIONS
)
from tools.ai_debate_auditor.engine import DebateAuditorEngine
from tools.ai_debate_auditor.models import (
    BoundaryViolation,
    PatternSeverity,
    EpistemicVerdict
)


class TestChallengerEmpiricalVerification(unittest.TestCase):
    """Empirical verification suite testing valid invariants and isolating failure modes."""

    def setUp(self):
        self.engine = DebateAuditorEngine()

    # =========================================================================
    # PART 1: VERIFIED ROBUST BEHAVIORS (PASSING INVARIANTS)
    # =========================================================================

    def test_pass_absolute_zero_bounds(self):
        """Verify Absolute Zero violations in Kelvin and Celsius."""
        # Violations (< 0 K or < -273.15 °C)
        self.assertTrue(len(verify_boundaries("The sample was cooled to -5 K.")) >= 1)
        self.assertTrue(len(verify_boundaries("The temperature reached -275 °C.")) >= 1)
        self.assertTrue(len(verify_boundaries("The core was at -300 C.")) >= 1)
        
        # Valid boundaries (>= 0 K and >= -273.15 °C)
        self.assertEqual(len(verify_boundaries("The quantum chip is cooled to 0 K.")), 0)
        self.assertEqual(len(verify_boundaries("Liquid nitrogen is at -196 °C.")), 0)
        self.assertEqual(len(verify_boundaries("Theoretical zero is -273.15 °C.")), 0)

    def test_pass_carnot_limit_basic_evaluations(self):
        """Verify Carnot limit calculation for single-sentence claims."""
        # 300K / 600K -> Carnot limit is 50%. Claim: 60% -> Violation
        v1 = verify_boundaries("An engine operating between 300 K and 600 K achieving 60% efficiency.")
        self.assertTrue(any("Carnot" in v.law_name for v in v1))

        # 300K / 600K -> Claim: 45% -> Valid (No violation)
        v2 = verify_boundaries("An engine operating between 300 K and 600 K achieving 45% efficiency.")
        self.assertEqual(len([v for v in v2 if "Carnot" in v.law_name]), 0)

    def test_pass_betz_limit_evaluations(self):
        """Verify Betz limit for open-flow wind turbines."""
        # Exceeding Betz limit (16/27 ≈ 59.3%) -> Violation
        v1 = verify_boundaries("The wind turbine extracts 75% of the kinetic wind energy.")
        self.assertTrue(any("Betz" in v.law_name for v in v1))

        # Sub-Betz limit -> Valid
        v2 = verify_boundaries("The wind turbine extracts 45% of the kinetic wind energy.")
        self.assertEqual(len([v for v in v2 if "Betz" in v.law_name]), 0)

    def test_pass_foundational_citations_and_proofs(self):
        """Verify LaTeX derivations and primary citations in synthesized counter-proofs."""
        violations = verify_boundaries("The engine achieves 150% efficiency.")
        proofs = synthesize_first_principles_counter_proofs(violations, [])
        self.assertTrue(len(proofs) >= 1)
        cp = proofs[0]
        self.assertIn("\\Delta U", cp.mathematical_derivation)
        self.assertIn("Carnot, S. (1824)", cp.primary_citations[0])


class TestEmpiricalFailureModesAndGaps(unittest.TestCase):
    """
    Verified remediation for empirical failure modes discovered during adversarial testing.
    These test cases confirm robust boundary verification in verifier.py.
    """

    def test_bug_1_carnot_multi_sentence_cross_contamination(self):
        """
        REMEDIATION 1: verifier.py Carnot regex properly scopes to intra-sentence boundaries,
        preventing false cross-contamination of temperatures across distinct sentences.
        """
        text = (
            "A combined cycle gas turbine operating between 300 K and 1400 K achieves 58% thermal efficiency. "
            "The system operates with 85% energy recovery."
        )
        violations = verify_boundaries(text)
        carnot_violations = [v for v in violations if "Carnot" in v.law_name]
        
        # Carnot limit for 300K/1400K is 78.6%. 58% is WELL BELOW 78.6%.
        # Verifier must NOT pair 300K/1400K with 85% from the next sentence.
        self.assertEqual(
            len(carnot_violations), 0,
            "Remediation 1: Carnot verifier must not produce false positive across sentence boundaries."
        )

    def test_bug_2_first_law_phrasing_false_negative(self):
        """
        REMEDIATION 2: verifier.py First Law regex successfully detects over-unity when phrased as
        'With an efficiency of 105%' or 'has an electrical efficiency of 150%'.
        """
        text = "With an efficiency of 105%, the system generates surplus electricity."
        violations = verify_boundaries(text)
        thermo_v = [v for v in violations if "First Law" in v.law_name]
        self.assertGreaterEqual(
            len(thermo_v), 1,
            "Remediation 2: 105% over-unity claim must be flagged as First Law violation."
        )

    def test_bug_3_special_relativity_passive_voice_false_negative(self):
        """
        REMEDIATION 3: verifier.py Special Relativity regex supports passive voice ('were recorded propagating at')
        and transitive verbs ('transmits signals at').
        """
        text1 = "The tachyonic signals were recorded propagating at 350000 km/s."
        violations1 = verify_boundaries(text1)
        rel_v1 = [v for v in violations1 if v.domain == "Special Relativity"]
        self.assertGreaterEqual(
            len(rel_v1), 1,
            "Remediation 3a: 'were recorded propagating at 350000 km/s' must be flagged as relativity violation."
        )

        text2 = "The system transmits monitoring signals at 500000 km/s to the base."
        violations2 = verify_boundaries(text2)
        rel_v2 = [v for v in violations2 if v.domain == "Special Relativity"]
        self.assertGreaterEqual(
            len(rel_v2), 1,
            "Remediation 3b: 'transmits monitoring signals at 500000 km/s' must be flagged as relativity violation."
        )

    def test_bug_4_kolmogorov_multi_word_event_false_negative(self):
        """
        REMEDIATION 4: verifier.py Kolmogorov regex supports multi-word events ('market growth', 'fatal system failure').
        """
        text = "The calculated probability of market growth is 125% next year."
        violations = verify_boundaries(text)
        prob_v = [v for v in violations if v.domain == "Probability Theory"]
        self.assertGreaterEqual(
            len(prob_v), 1,
            "Remediation 4: 'probability of market growth is 125%' must be flagged as Kolmogorov violation."
        )

    def test_landauer_bound_zero_dissipation(self):
        """
        REMEDIATION 5: verifier.py detects Landauer bound violations on zero-dissipation bit erasure claims.
        """
        text = "Our quantum computer achieved irreversible bit erasure with zero energy dissipation."
        violations = verify_boundaries(text)
        landauer_v = [v for v in violations if "Landauer" in v.law_name]
        self.assertGreaterEqual(
            len(landauer_v), 1,
            "Remediation 5: Zero-dissipation irreversible bit erasure must be flagged under Landauer's bound."
        )


if __name__ == "__main__":
    unittest.main()
