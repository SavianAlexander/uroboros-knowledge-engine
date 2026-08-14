"""
Counter-Argument Synthesizer Engine (R3) for Adversarial AI Debate Auditor.
Structural mechanism failure breakdown, real-world friction/entropy injection,
deductive first-principles counter-proof synthesis, and sharp Socratic stress-test questions.
"""

from typing import List, Dict, Any, Optional
from .models import (
    Claim,
    PatternMatch,
    BoundaryViolation,
    CitationCheck,
    MechanismFailure,
    CounterProof,
    CounterArgumentSynthesis,
    PatternType
)


# Primary Literature Registry for First-Principles Refutations
PRIMARY_FOUNDATIONAL_CITATIONS = {
    "Thermodynamics": [
        "Carnot, S. (1824). Réflexions sur la puissance motrice du feu et sur les machines propres à développer cette puissance. Bachelier, Paris.",
        "Clausius, R. (1850). Ueber die bewegende Kraft der Wärme. Annalen der Physik, 155(3), 368-397.",
        "Kelvin, Lord (1851). On the Dynamical Theory of Heat. Transactions of the Royal Society of Edinburgh, 20, 261-288."
    ],
    "Special Relativity": [
        "Einstein, A. (1905). Zur Elektrodynamik bewegter Körper. Annalen der Physik, 322(10), 891-921. doi:10.1002/andp.19053221004"
    ],
    "Information Theory": [
        "Shannon, C. E. (1948). A Mathematical Theory of Communication. Bell System Technical Journal, 27(3), 379-423.",
        "Landauer, R. (1961). Irreversibility and Heat Generation in the Computing Process. IBM Journal of Research and Development, 5(3), 183-191."
    ],
    "Probability Theory": [
        "Kolmogorov, A. N. (1933). Grundbegriffe der Wahrscheinlichkeitsrechnung. Springer, Berlin."
    ],
    "Computational Complexity": [
        "Knuth, D. E. (1998). The Art of Computer Programming, Vol. 3: Sorting and Searching (2nd ed.). Addison-Wesley.",
        "Amdahl, G. M. (1967). Validity of the single processor approach to achieving large scale computing capabilities. AFIPS Conf. Proc., 30, 483-485."
    ],
    "Fluid Dynamics": [
        "Betz, A. (1920). Das Maximum der theoretisch möglichen Ausnützung des Windes durch Windmotoren. Zeitschrift für das Gesamte Turbinenwesen, 26, 307-309."
    ]
}


def build_mechanism_failure_breakdowns(
    claims: List[Claim],
    fallacies: List[PatternMatch],
    boundary_violations: List[BoundaryViolation]
) -> List[MechanismFailure]:
    """
    Construct step-by-step mechanism failure decompositions for flawed or ungrounded claims.
    """
    failures: List[MechanismFailure] = []
    
    # 1. Process Boundary Violations
    for b in boundary_violations:
        failures.append(
            MechanismFailure(
                target_claim=b.claim_snippet or f"{b.law_name} ({b.claimed_value})",
                premises=[
                    f"Assumes system operates with claimed parameter: {b.claimed_value}",
                    f"Assumes zero dissipation or bypass of {b.first_principle_law}"
                ],
                causal_steps=[
                    "Step 1: Input energy/information enters closed control volume.",
                    "Step 2: Conversion/transmission occurs across state boundary.",
                    f"Step 3 (BREAK): Output exceeds theoretical ceiling {b.theoretical_limit}, requiring unphysical negative entropy or superluminal causality."
                ],
                fatal_leap=f"Asserts violation of {b.law_name} without accounting for {b.delta_violation}.",
                omitted_friction=[
                    "Thermal dissipation (Joule heating / resistive loss)",
                    "Entropy generation (Second Law irreversible entropy production delta S_irr > 0)",
                    "Parasitic impedance and friction drag"
                ],
                scaling_bottlenecks=[
                    "Thermal runaway at power density threshold",
                    "Dissipation scaling proportional to quadratic current/load"
                ]
            )
        )

    # 2. Process Logical / Structural Fallacies
    for f in fallacies:
        if f.pattern_id == PatternType.P06_CIRCULAR_LOGIC:
            failures.append(
                MechanismFailure(
                    target_claim=f.snippet[:120],
                    premises=[
                        "Premise A: System possesses property X by definition.",
                        "Premise B: Property X is cited as proof that system produces outcome Y."
                    ],
                    causal_steps=[
                        "Step 1: Declare conclusion in initial definition.",
                        "Step 2: Traverse circular reasoning loop back to definition.",
                        "Step 3 (BREAK): No independent physical or algorithmic transfer mechanism provided."
                    ],
                    fatal_leap="Petitio principii: Equates the premise with the conclusion without empirical verification.",
                    omitted_friction=["Verification complexity", "Empirical edge-case testing"],
                    scaling_bottlenecks=["Failure under adversarial testing and independent observation"]
                )
            )
        elif f.pattern_id == PatternType.P09_SPURIOUS_CAUSATION:
            failures.append(
                MechanismFailure(
                    target_claim=f.snippet[:120],
                    premises=[
                        "Observation 1: Event A precedes or correlates with Event B.",
                        "Assertion: Event A is the singular causal driver of Event B."
                    ],
                    causal_steps=[
                        "Step 1: Measure temporal succession t(A) < t(B) or statistical covariance.",
                        "Step 2 (BREAK): Omit confounding variables and counterfactual baseline testing.",
                        "Step 3: Conclude direct causal mechanism."
                    ],
                    fatal_leap="Cum hoc / post hoc ergo propter hoc: Confounds covariance with causal transmission.",
                    omitted_friction=["Latent confounding variables", "Seasonal/cyclical co-variance"],
                    scaling_bottlenecks=["Model collapse when applied to out-of-distribution environments"]
                )
            )

    # Fallback if no specific failure generated but claims exist
    if not failures and claims:
        # Find first unsubstantiated claim
        unsub = next((c for c in claims if c.unsubstantiated), claims[0])
        failures.append(
            MechanismFailure(
                target_claim=unsub.text,
                premises=["Premise 1: Direct assertion without primary literature citations."],
                causal_steps=[
                    "Step 1: Stated proposition without parameter constraints.",
                    "Step 2 (BREAK): Unsubstantiated leap from premise to universal validity."
                ],
                fatal_leap="Lacks empirical error bounds and falsifiable operational criteria.",
                omitted_friction=["Operational variance", "System overhead"],
                scaling_bottlenecks=["Non-linear performance degradation at scale"]
            )
        )

    return failures


def generate_friction_points(
    boundary_violations: List[BoundaryViolation],
    fallacies: List[PatternMatch]
) -> List[str]:
    """
    Generate domain-specific physical, computational, and institutional friction points.
    """
    frictions: List[str] = []
    
    # Check for thermodynamics/physics
    has_physics = any(b.domain == "Thermodynamics" for b in boundary_violations)
    if has_physics:
        frictions.append("Thermodynamic Dissipation: In any non-ideal real-world process, irreversible entropy generation (dS > 0) creates thermal dissipation and parasitic resistance.")
        frictions.append("Thermal Gradient Bottleneck: Heat exchange rates are bounded by Fourier conduction (q = -k dT/dx) and finite surface area transfer limits.")

    # Check for distributed systems / latency
    has_relativity = any(b.domain == "Special Relativity" for b in boundary_violations)
    if has_relativity or any("latency" in f.snippet.lower() for f in fallacies):
        frictions.append("Optical Propagation Delay: Speed of light in single-mode silica fiber (~200,000 km/s) imposes an immutable ~5 ms round-trip time per 1,000 km.")
        frictions.append("Serialization & Queueing Overhead: Buffer contention, packet jitter, and TCP handshake retransmissions induce non-zero p99 latency spikes.")

    # Concurrency / Scaling friction
    frictions.append("Concurrency & Lock Contention: As parallel node count N increases, Universal Scalability Law overhead (coherency penalty beta * N * (N - 1)) causes retrograde throughput degradation.")
    frictions.append("Economic & Transaction Costs: Real-world operational coordination incurs nonzero verification, monitoring, and principal-agent alignment overhead.")
    
    return frictions


def generate_socratic_questions(
    claims: List[Claim],
    fallacies: List[PatternMatch],
    boundary_violations: List[BoundaryViolation],
    citations: List[CitationCheck]
) -> List[str]:
    """
    Generate sharp, falsification-focused Socratic questions targeting logical and empirical gaps.
    """
    questions: List[str] = []
    
    # 1. Falsification trigger
    questions.append(
        "Falsification Trigger: Under what precise, measurable empirical conditions or threshold metrics would this proposition be conclusively proven false?"
    )
    
    # 2. Mechanism probe
    if boundary_violations:
        bv = boundary_violations[0]
        questions.append(
            f"Physical Mechanism Probe: By what exact thermodynamic or physical transfer function does the system circumvent {bv.law_name} without generating positive irreversible entropy?"
        )
    else:
        questions.append(
            "Intermediate Mechanism Probe: What is the step-by-step causal transfer function that transitions state A to state B, and how are intermediate loss factors accounted for?"
        )

    # 3. Scaling challenge
    questions.append(
        "Scaling Stress-Test: When system concurrency or operational load scales by 10^3, how does the architecture prevent quadratic coordination bottlenecks and latency degradation?"
    )

    # 4. Phantom citation / empirical grounding challenge
    phantom_cites = [c for c in citations if c.is_phantom]
    if phantom_cites:
        questions.append(
            f"Citation Forensics: What specific, indexed peer-reviewed journal volume and page numbers verify the claims attributed to '{phantom_cites[0].raw_citation}'?"
        )

    # 5. Sycophancy / bias challenge
    if any(f.pattern_id == PatternType.P01_SYCOPHANCY for f in fallacies):
        questions.append(
            "Presupposition Challenge: If the user's initial framing assumption is inverted, what empirical counter-evidence immediately emerges?"
        )

    return questions


def synthesize_first_principles_counter_proofs(
    boundary_violations: List[BoundaryViolation],
    fallacies: List[PatternMatch]
) -> List[CounterProof]:
    """
    Synthesize formal deductive mathematical and logical counter-proofs.
    """
    proofs: List[CounterProof] = []
    
    for b in boundary_violations:
        if "First Law" in b.law_name:
            proofs.append(
                CounterProof(
                    target_claim=b.claim_snippet or f"Energy Efficiency Claim: {b.claimed_value}",
                    implicit_assumption="Assumes net work output can exceed heat/power input in a closed steady-state cycle without mass/fuel consumption.",
                    empirical_axiom="First Law of Thermodynamics (Conservation of Energy): Delta U = Q - W. For steady-state closed systems, Delta U = 0 => W_out <= Q_in.",
                    mathematical_derivation=(
                        "\\Delta U = Q_{in} - W_{out} = 0 \\implies W_{out} = Q_{in} - Q_{dissipated}\n"
                        "\\text{Since } Q_{dissipated} \\ge 0 \\implies W_{out} \\le Q_{in}\n"
                        "\\eta = \\frac{W_{out}}{Q_{in}} \\le 1.00 \\quad (100\\%)\n"
                        "\\text{Claimed } \\eta = " + b.claimed_value + " > 100\\% \\implies \\text{CONTRADICTION}"
                    ),
                    refutation_conclusion=f"The claim {b.claimed_value} is mathematically and physically impossible under axiomatic conservation of energy.",
                    primary_citations=PRIMARY_FOUNDATIONAL_CITATIONS.get("Thermodynamics", [])
                )
            )
        elif "Carnot" in b.law_name:
            proofs.append(
                CounterProof(
                    target_claim=b.claim_snippet or f"Carnot Efficiency Claim: {b.claimed_value}",
                    implicit_assumption="Assumes heat engine can operate with zero entropy generation between finite thermal reservoirs.",
                    empirical_axiom="Second Law of Thermodynamics (Carnot Theorem): No heat engine operating between reservoirs at T_hot and T_cold can exceed eta_max = 1 - (T_cold / T_hot).",
                    mathematical_derivation=(
                        "\\oint \\frac{\\delta Q}{T} \\le 0 \\implies \\frac{Q_{in}}{T_H} - \\frac{Q_{out}}{T_C} \\le 0\n"
                        "\\implies \\eta = 1 - \\frac{Q_{out}}{Q_{in}} \\le 1 - \\frac{T_C}{T_H} = \\eta_{Carnot}\n"
                        "\\text{Claimed } \\eta = " + b.claimed_value + " > " + b.theoretical_limit + " \\implies \\text{CONTRADICTION}"
                    ),
                    refutation_conclusion=f"The claim of {b.claimed_value} exceeds the maximum theoretical Carnot limit of {b.theoretical_limit}.",
                    primary_citations=PRIMARY_FOUNDATIONAL_CITATIONS.get("Thermodynamics", [])
                )
            )
        elif "Speed of Light" in b.law_name or "Special Relativity" in b.domain:
            proofs.append(
                CounterProof(
                    target_claim=b.claim_snippet or f"Superluminal Signaling Claim: {b.claimed_value}",
                    implicit_assumption="Assumes information or physical particles can propagate with velocity v > c in vacuum.",
                    empirical_axiom="Special Relativity (Lorentz Invariance): The relativistic mass-energy relation E = gamma * m * c^2 requires infinite energy as v -> c.",
                    mathematical_derivation=(
                        "\\gamma = \\frac{1}{\\sqrt{1 - v^2 / c^2}}\n"
                        "\\lim_{v \\to c^-} \\gamma = \\infty \\implies E = \\gamma m_0 c^2 \\to \\infty\n"
                        "\\text{For } v > c, \\sqrt{1 - v^2 / c^2} \\in \\mathbb{C} \\implies \\text{Imaginary Mass/Energy (Unphysical)}"
                    ),
                    refutation_conclusion=f"Propagation velocity {b.claimed_value} violates relativistic causality and requires infinite energy.",
                    primary_citations=PRIMARY_FOUNDATIONAL_CITATIONS.get("Special Relativity", [])
                )
            )
        elif "Kolmogorov" in b.law_name or "Probability" in b.domain:
            proofs.append(
                CounterProof(
                    target_claim=b.claim_snippet or f"Probability Claim: {b.claimed_value}",
                    implicit_assumption="Assumes probability measure can take values outside the unit interval [0, 1].",
                    empirical_axiom="Kolmogorov Probability Measure Axioms (1933): For any event E in sample space Omega, 0 <= P(E) <= 1 and P(Omega) = 1.",
                    mathematical_derivation=(
                        "P: \\mathcal{F} \\to [0, 1] \\implies \\forall E \\in \\mathcal{F}, \\; 0.0 \\le P(E) \\le 1.0\n"
                        "\\text{Claimed value } " + b.claimed_value + " \\notin [0.0, 1.0] \\implies \\text{AXIOM VIOLATION}"
                    ),
                    refutation_conclusion=f"Probability value {b.claimed_value} is mathematically ill-formed under measure theory.",
                    primary_citations=PRIMARY_FOUNDATIONAL_CITATIONS.get("Probability Theory", [])
                )
            )
        elif "Betz" in b.law_name or "Fluid Dynamics" in b.domain:
            proofs.append(
                CounterProof(
                    target_claim=b.claim_snippet or f"Wind Turbine Extraction Claim: {b.claimed_value}",
                    implicit_assumption="Assumes open actuator disk can extract kinetic fluid energy without mass deceleration and back-pressure divergence.",
                    empirical_axiom="Betz's Law (1920): Maximum open-flow kinetic power coefficient C_p = 16/27 ≈ 59.26% under axial momentum theory.",
                    mathematical_derivation=(
                        "C_p = 4a(1-a)^2 \\quad \\text{where } a = \\text{axial induction factor}\n"
                        "\\frac{d C_p}{da} = 4(1-a)(1-3a) = 0 \\implies a = \\frac{1}{3}\n"
                        "C_{p,\\max} = 4\\left(\\frac{1}{3}\\right)\\left(\\frac{2}{3}\\right)^2 = \\frac{16}{27} \\approx 59.26\\%\n"
                        "\\text{Claimed } \\eta = " + b.claimed_value + " > 59.26\\% \\implies \\text{CONTRADICTION}"
                    ),
                    refutation_conclusion=f"Energy extraction efficiency {b.claimed_value} exceeds the maximum theoretical Betz ceiling (59.3%).",
                    primary_citations=PRIMARY_FOUNDATIONAL_CITATIONS.get("Fluid Dynamics", [])
                )
            )
        elif "Landauer" in b.law_name or "Information" in b.domain:
            proofs.append(
                CounterProof(
                    target_claim=b.claim_snippet or f"Information Erasure Claim: {b.claimed_value}",
                    implicit_assumption="Assumes logical many-to-one state transitions (bit erasure) can occur without environmental entropy generation.",
                    empirical_axiom="Landauer's Principle (1961): Erasing 1 bit of information in any irreversible computing process requires a minimum thermodynamic energy dissipation of E >= k_B * T * ln(2).",
                    mathematical_derivation=(
                        "\\Delta S_{system} = -k_B \\ln 2 \\implies \\Delta S_{env} \\ge k_B \\ln 2\n"
                        "Q = T \\Delta S_{env} \\ge k_B T \\ln 2 \\approx 2.87 \\times 10^{-21} \\text{ J at } 300\\text{ K}\n"
                        "\\text{Claimed } E = 0 \\implies \\Delta S_{total} < 0 \\implies \\text{SECOND LAW CONTRADICTION}"
                    ),
                    refutation_conclusion="Zero-dissipation irreversible bit erasure violates Landauer's bound and the Second Law of Thermodynamics.",
                    primary_citations=PRIMARY_FOUNDATIONAL_CITATIONS.get("Information Theory", [])
                )
            )

    # If no boundary violations exist, synthesize a deductive logical counter-proof against circular or inflated claims
    if not proofs:
        for f in fallacies:
            if f.pattern_id == PatternType.P07_QUANTIFIER_INFLATION:
                proofs.append(
                    CounterProof(
                        target_claim=f.snippet,
                        implicit_assumption="Assumes universal proposition holds across all unbounded domain states without empirical exceptions.",
                        empirical_axiom="Popperian Epistemology & Epistemic Logic: A universal statement forall x in X (P(x)) is invalidated by a single counter-example exists x (not P(x)).",
                        mathematical_derivation=(
                            "\\forall x \\in \\mathcal{D}, \\; P(x) = 1.00\n"
                            "\\text{In any stochastic real-world system with variance } \\sigma^2 > 0:\n"
                            "P(\\exists x : \\neg P(x)) = 1 - \\prod (1 - p_i) > 0 \\implies \\text{Universal certainty is falsified.}"
                        ),
                        refutation_conclusion="Universal absolute claims collapse under real-world non-zero variance and boundary edge conditions.",
                        primary_citations=["Popper, K. (1934). Logik der Forschung. Springer, Vienna."]
                    )
                )
                break

    return proofs


def synthesize_counter_arguments(
    claims: List[Claim],
    fallacies: List[PatternMatch],
    boundary_violations: List[BoundaryViolation],
    citations: List[CitationCheck]
) -> CounterArgumentSynthesis:
    """
    Synthesize comprehensive adversarial counter-argument suite.
    """
    mechanism_breakdowns = build_mechanism_failure_breakdowns(claims, fallacies, boundary_violations)
    friction_points = generate_friction_points(boundary_violations, fallacies)
    socratic_questions = generate_socratic_questions(claims, fallacies, boundary_violations, citations)
    counter_proofs = synthesize_first_principles_counter_proofs(boundary_violations, fallacies)
    
    return CounterArgumentSynthesis(
        mechanism_breakdowns=mechanism_breakdowns,
        friction_points=friction_points,
        socratic_questions=socratic_questions,
        deductive_counter_proofs=counter_proofs
    )
