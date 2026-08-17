"""
Unit and Integration Test Suite for Architectural Modernization:
- Domain Plugin SPI & Registry
- Dynamic Composable RAG DAG Pipeline
- Autonomous Knowledge Synthesis Loop
- Strategy Pattern Registry
"""

import pytest
import sqlite3
import time
from src.core.domain_plugin_spi import (
    BaseDomainPlugin,
    DomainPluginManifest,
    DomainRegistry,
    get_domain_registry
)
from src.domain.retrieval_pipeline_dag import (
    RetrievalDAGPipeline,
    get_retrieval_pipeline
)
from src.domain.knowledge_synthesis_loop import (
    KnowledgeSynthesisLoop,
    get_knowledge_synthesis_loop
)
from src.infrastructure.retrieval_strategies import (
    BaseRetrievalStrategy,
    StrategyRegistry,
    get_strategy_registry
)


def test_domain_plugin_spi_registration():
    registry = get_domain_registry()
    plugins = registry.list_plugins()
    assert len(plugins) >= 1
    
    # Check PR legal or EVE plugin
    handler = registry.find_handler("What is the statute in Puerto Rico Código Civil?")
    assert handler is not None
    assert "puerto_rico" in handler.manifest.name.lower()
    prompt_ext = handler.get_system_prompt_extension("test query")
    assert prompt_ext is not None


def test_retrieval_dag_pipeline_execution():
    pipeline = get_retrieval_pipeline()
    res = pipeline.execute("Explain Clean Architecture principles and SQLite WAL mode", enable_web=False)
    assert res is not None
    assert res.metrics.total_duration_ms >= 0.0
    assert len(res.metrics.stages_executed) >= 1
    assert "stage_1_intent" in res.metrics.stage_latencies_ms


def test_knowledge_synthesis_loop():
    synth = get_knowledge_synthesis_loop()
    
    user_query = "How to implement Clean Architecture in Python?"
    assistant_response = (
        "## Clean Architecture in Python\n\n"
        "Clean Architecture enforces layer decoupling between Presentation, Routers, Domain, and Infrastructure.\n"
        "- Presentation Layer: UI components\n"
        "- Domain Layer: Business rules and [[GraphRAG]]\n"
        "- Infrastructure: SQLite [[database]] and [[vector_engine]]\n\n"
        "```python\n"
        "def example():\n"
        "    pass\n"
        "```\n\n"
        "Key Takeaways: Always depend inwards."
    )
    
    assert synth.should_synthesize(user_query, assistant_response) is True
    
    entities = synth.extract_entities_and_wikilinks(assistant_response)
    assert "GraphRAG" in entities or "database" in entities or "Clean" in entities
    
    rec = synth.record_synthesis(session_id=999, user_query=user_query, assistant_response=assistant_response)
    assert rec is not None
    assert rec["filepath"].startswith("synthesis/")
    assert len(rec["sha256"]) == 64


def test_strategy_registry():
    registry = get_strategy_registry()
    
    class MockCustomStrategy(BaseRetrievalStrategy):
        @property
        def name(self) -> str:
            return "mock_strategy"
            
        def execute(self, query: str, top_k: int = 10, **kwargs):
            return [{"title": "Mock Hit", "score": 1.0}]
            
    registry.register(MockCustomStrategy())
    assert registry.get("mock_strategy") is not None
    res = registry.execute("mock_strategy", "test query", top_k=5)
    assert len(res) == 1
    assert res[0]["title"] == "Mock Hit"
