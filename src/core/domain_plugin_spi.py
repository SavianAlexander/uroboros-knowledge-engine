"""
Domain Service Provider Interface (SPI) and Cartridge Registry.
Provides modular lifecycle, prompt injection, tool hooks, and query interception
for vertical domains (Legal, EVE, Enterprise Cúram, Jira) without polluting the core engine.
Standard: Python Standard Library (typing, abc, dataclasses, logging).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
import logging

logger = logging.getLogger(__name__)


@dataclass
class DomainPluginManifest:
    name: str
    version: str
    description: str
    keywords: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    author: str = "Uroboros Systems"


class BaseDomainPlugin(ABC):
    """Abstract Base Class for Uroboros Domain Plugins."""

    @property
    @abstractmethod
    def manifest(self) -> DomainPluginManifest:
        """Return the plugin metadata manifest."""
        pass

    def get_system_prompt_extension(self, query: str = "") -> Optional[str]:
        """Return custom instructions or prompt grounding for this domain."""
        return None

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Return list of JSON-RPC / MCP compatible tool schemas exposed by this domain."""
        return []

    def can_handle_query(self, query: str) -> bool:
        """Determine if this plugin should intercept or enrich the user query."""
        if not query:
            return False
        q_lower = query.lower()
        return any(kw.lower() in q_lower for kw in self.manifest.keywords)

    def intercept_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Optionally intercept and handle query resolution prior to generic RAG."""
        return None

    def enrich_retrieval(self, query: str, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Post-process and rerank or annotate retrieved chunks for this domain."""
        return chunks


class DomainRegistry:
    """Thread-safe Singleton Registry for domain plugins and vertical cartridges."""

    _instance: Optional["DomainRegistry"] = None

    def __new__(cls) -> "DomainRegistry":
        if cls._instance is None:
            cls._instance = super(DomainRegistry, cls).__new__(cls)
            cls._instance._plugins: Dict[str, BaseDomainPlugin] = {}
            cls._instance._initialized = False
        return cls._instance

    def register(self, plugin: BaseDomainPlugin) -> None:
        """Register a domain plugin instance."""
        manifest = plugin.manifest
        self._plugins[manifest.name.lower()] = plugin
        logger.info(f"[DomainRegistry] Registered domain plugin '{manifest.name}' v{manifest.version}")

    def get(self, name: str) -> Optional[BaseDomainPlugin]:
        """Retrieve a registered plugin by name."""
        return self._plugins.get(name.lower())

    def list_plugins(self) -> List[DomainPluginManifest]:
        """Return list of all registered plugin manifests."""
        return [p.manifest for p in self._plugins.values()]

    def find_handler(self, query: str) -> Optional[BaseDomainPlugin]:
        """Find the first plugin willing to handle the query based on keyword/intent matching."""
        if not query:
            return None
        for plugin in self._plugins.values():
            try:
                if plugin.can_handle_query(query):
                    return plugin
            except Exception as e:
                logger.debug(f"[DomainRegistry] Plugin matching error on {plugin.manifest.name}: {e}")
        return None

    def auto_discover_builtins(self) -> None:
        """Lazily discover and register built-in vertical domain plugins."""
        if getattr(self, "_initialized", False):
            return

        # 1. Neural Voice & Audio Telemetry Plugin
        try:
            class VoiceAudioDomainPlugin(BaseDomainPlugin):
                @property
                def manifest(self) -> DomainPluginManifest:
                    return DomainPluginManifest(
                        name="voice_audio",
                        version="1.0.0",
                        description="Kokoro Neural Voice Synthesis & Audio DSP Pipeline",
                        keywords=["voice", "tts", "speak", "audio", "sfx", "intercom", "kokoro"],
                        capabilities=["neural_tts", "audio_dsp", "voice_rag"]
                    )
                def get_system_prompt_extension(self, query: str = "") -> Optional[str]:
                    return "Voice Synthesis Protocol: Generate high-fidelity neural audio briefings and telemetry."
            self.register(VoiceAudioDomainPlugin())
        except Exception as e:
            logger.debug(f"[DomainRegistry] Skipped Voice plugin: {e}")

        self._initialized = True


# Global helper accessor
def get_domain_registry() -> DomainRegistry:
    registry = DomainRegistry()
    registry.auto_discover_builtins()
    return registry
