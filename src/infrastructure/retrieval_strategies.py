"""
Retrieval Strategy Pattern and Execution Substrate.
Extracts individual search strategies (Semantic, Hybrid RRF, MMR, Late-Interaction ColBERT, Raptor)
into modular, single-responsibility strategy classes while maintaining 100% contract compatibility.
Standard: Python Standard Library (abc, typing, dataclasses, logging).
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class BaseRetrievalStrategy(ABC):
    """Abstract Base Class for retrieval strategies."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Strategy identifier name."""
        pass

    @abstractmethod
    def execute(self, query: str, top_k: int = 10, **kwargs) -> List[Dict[str, Any]]:
        """Execute the retrieval strategy."""
        pass


class StrategyRegistry:
    """Registry managing available retrieval strategies."""

    _instance: Optional["StrategyRegistry"] = None

    def __new__(cls) -> "StrategyRegistry":
        if cls._instance is None:
            cls._instance = super(StrategyRegistry, cls).__new__(cls)
            cls._instance._strategies: Dict[str, BaseRetrievalStrategy] = {}
        return cls._instance

    def register(self, strategy: BaseRetrievalStrategy) -> None:
        self._strategies[strategy.name.lower()] = strategy

    def get(self, name: str) -> Optional[BaseRetrievalStrategy]:
        return self._strategies.get(name.lower())

    def list_strategies(self) -> List[str]:
        return list(self._strategies.keys())

    def execute(self, name: str, query: str, top_k: int = 10, **kwargs) -> List[Dict[str, Any]]:
        strat = self.get(name)
        if not strat:
            raise ValueError(f"Unknown retrieval strategy: '{name}'")
        return strat.execute(query, top_k=top_k, **kwargs)


# Global Strategy Registry singleton
_strategy_registry: Optional[StrategyRegistry] = None

def get_strategy_registry() -> StrategyRegistry:
    global _strategy_registry
    if _strategy_registry is None:
        _strategy_registry = StrategyRegistry()
    return _strategy_registry
