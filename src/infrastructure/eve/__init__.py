"""
Unified EVE Online Infrastructure & Telemetry Subsystem.
Consolidates ESI API clients, SDE static data caches, SSO token workflows,
market arbitrage calculation, EFT fitting parsers, and tactical radar telemetry.
"""

from typing import Dict, Any, List, Optional

# ESI & SSO Auth
try:
    from src.infrastructure.eve_esi import EveEsiClient, get_character_info, get_system_kills
except ImportError:
    EveEsiClient = None
    get_character_info = None
    get_system_kills = None

try:
    from src.infrastructure.eve_sso import EveSsoManager
except ImportError:
    EveSsoManager = None

# SDE Static Data
try:
    from src.infrastructure.eve_sde import EveSdeDatabase, get_type_name
except ImportError:
    EveSdeDatabase = None
    get_type_name = None

# Market & Industry
try:
    from src.infrastructure.eve_market import EveMarketEngine, get_market_orders
except ImportError:
    EveMarketEngine = None
    get_market_orders = None

try:
    from src.infrastructure.eve_arbitrage import calculate_station_arbitrage
except ImportError:
    calculate_station_arbitrage = None

# Combat Mechanics & Fitting
try:
    from src.infrastructure.eve_eft_parser import parse_eft_fit, EftFitting
except ImportError:
    parse_eft_fit = None
    EftFitting = None

try:
    from src.infrastructure.eve_combat_simulator import simulate_ship_combat
except ImportError:
    simulate_ship_combat = None

# Voice Radar & Telemetry
try:
    from src.infrastructure.eve_voice_copilot import EveVoiceCopilot
except ImportError:
    EveVoiceCopilot = None

try:
    from src.infrastructure.eve_voice_radar_daemon import EveRadarDaemon
except ImportError:
    EveRadarDaemon = None


__all__ = [
    "EveEsiClient",
    "get_character_info",
    "get_system_kills",
    "EveSsoManager",
    "EveSdeDatabase",
    "get_type_name",
    "EveMarketEngine",
    "get_market_orders",
    "calculate_station_arbitrage",
    "parse_eft_fit",
    "EftFitting",
    "simulate_ship_combat",
    "EveVoiceCopilot",
    "EveRadarDaemon"
]
