"""
Pillar 3: Synthesis & Generation Domain Subpackage.
Encapsulates Anki flashcard generation, synthetic Q&A generation, executive/daily briefings,
knowledge distillation, code refactoring, diff synthesis, wikilink parsing, and graph visualization.
"""
from src.domain.anki_card_synthesizer import (
    AnkiCardSynthesizer,
    generate_anki_cards_from_text,
    export_anki_apkg_deck,
)
from src.domain.synthetic_qa_generator import (
    SyntheticQAGenerator,
    generate_synthetic_qa_pairs,
)
from src.domain.executive_briefing import (
    ExecutiveBriefingSynthesizer,
    generate_executive_briefing,
)
from src.domain.daily_briefing import (
    DailyBriefingSynthesizer,
    generate_daily_briefing,
)
from src.domain.audio_briefing import (
    AudioBriefingSynthesizer,
    generate_audio_briefing_script,
)
from src.domain.faq_synthesizer import (
    FAQSynthesizer,
    generate_vault_faqs,
)
from src.domain.extractive_summarizer import (
    ExtractiveSummarizer,
    summarize_text,
)
from src.domain.knowledge_distiller import (
    KnowledgeDistiller,
    distill_document_concepts,
)
from src.domain.knowledge_synthesis_loop import (
    KnowledgeSynthesisLoop,
    run_synthesis_cycle,
)
from src.domain.dataset_synthesizer import DatasetSynthesizer
from src.domain.code_diff_synthesizer import synthesize_code_diff
from src.domain.code_self_refactor import refactor_code_ast
from src.domain.code_doc_aligner import align_code_and_documentation
from src.domain.graph_link_synthesizer import synthesize_graph_links
from src.domain.graph_mermaid_generator import generate_mermaid_graph
from src.domain.wikilink_parser import extract_wikilinks, build_wikilink_graph
from src.domain.citation_deep_linker import create_deep_citation_link
from src.domain.relational_schema_linker import RelationalSchemaLinker
from src.domain.synthesis.merkle_provenance import (
    MerkleProvenanceEngine,
    generate_merkle_provenance,
    verify_merkle_provenance,
)
from src.domain.graph_engine import compute_graph_pagerank, export_graph_to_graphml

__all__ = [
    "AnkiCardSynthesizer",
    "generate_anki_cards_from_text",
    "export_anki_apkg_deck",
    "SyntheticQAGenerator",
    "generate_synthetic_qa_pairs",
    "ExecutiveBriefingSynthesizer",
    "generate_executive_briefing",
    "DailyBriefingSynthesizer",
    "generate_daily_briefing",
    "AudioBriefingSynthesizer",
    "generate_audio_briefing_script",
    "FAQSynthesizer",
    "generate_vault_faqs",
    "ExtractiveSummarizer",
    "summarize_text",
    "KnowledgeDistiller",
    "distill_document_concepts",
    "KnowledgeSynthesisLoop",
    "run_synthesis_cycle",
    "DatasetSynthesizer",
    "synthesize_code_diff",
    "refactor_code_ast",
    "align_code_and_documentation",
    "synthesize_graph_links",
    "generate_mermaid_graph",
    "extract_wikilinks",
    "build_wikilink_graph",
    "create_deep_citation_link",
    "RelationalSchemaLinker",
    "compute_graph_pagerank",
    "export_graph_to_graphml",
    "MerkleProvenanceEngine",
    "generate_merkle_provenance",
    "verify_merkle_provenance",
]
