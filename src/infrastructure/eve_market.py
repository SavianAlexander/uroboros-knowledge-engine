"""
EVE Online Market Valuation & Price Engine.

Fetches live universe price averages and adjusted prices from ESI (/markets/prices/),
computes real-time ISK valuations for asset hangars, ship fittings, and blueprints,
and determines exact pilot and fleet Net Worth.

Ponytail: Zero-dependency stdlib implementation (urllib, json, time, os).
"""

import os
import sys
import json
import time
import urllib.request
import urllib.parse
import urllib.error

ESI_BASE = "https://esi.evetech.net/latest"
USER_AGENT = "Uroboros-Knowledge-Engine/2.0 (Market Valuation; contact: admin@uroboros.local)"

PRICE_CACHE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "vault",
    "Eve Online",
    "market_prices.json"
)

_cached_prices = None
_last_fetch_time = 0


def fetch_universe_market_prices(max_cache_age_seconds: int = 3600) -> dict:
    """Fetch or load cached adjusted & average market prices for all EVE type IDs."""
    global _cached_prices, _last_fetch_time

    now = time.time()
    if _cached_prices is not None and (now - _last_fetch_time) < max_cache_age_seconds:
        return _cached_prices

    # Check disk cache
    if os.path.exists(PRICE_CACHE_PATH):
        try:
            mtime = os.path.getmtime(PRICE_CACHE_PATH)
            if (now - mtime) < max_cache_age_seconds:
                with open(PRICE_CACHE_PATH, "r", encoding="utf-8") as f:
                    _cached_prices = json.load(f)
                    _last_fetch_time = mtime
                    return _cached_prices
        except Exception:
            pass

    # Fetch live from ESI /markets/prices/
    url = f"{ESI_BASE}/markets/prices/"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            price_map = {}
            if isinstance(data, list):
                for item in data:
                    tid = item.get("type_id")
                    if tid:
                        avg_p = item.get("average_price") or item.get("adjusted_price") or 0.0
                        adj_p = item.get("adjusted_price") or item.get("average_price") or 0.0
                        price_map[str(tid)] = {
                            "average_price": float(avg_p),
                            "adjusted_price": float(adj_p),
                        }

            _cached_prices = price_map
            _last_fetch_time = now

            os.makedirs(os.path.dirname(PRICE_CACHE_PATH), exist_ok=True)
            with open(PRICE_CACHE_PATH, "w", encoding="utf-8") as f:
                json.dump(price_map, f)

            return price_map
    except Exception as ex:
        print(f"⚠️ Failed to fetch live market prices: {ex}")
        return _cached_prices or {}


def get_item_price(type_id: int, prices: dict = None) -> float:
    """Get average market price for a type ID."""
    if prices is None:
        prices = fetch_universe_market_prices()
    info = prices.get(str(type_id), {})
    return info.get("average_price", 0.0) or info.get("adjusted_price", 0.0)


def compute_asset_valuation(items: list, prices: dict = None, top_k: int = 10) -> dict:
    """Compute total valuation and top value items from an asset list with single-pass aggregation."""
    if prices is None:
        prices = fetch_universe_market_prices()

    total_value = 0.0
    valued_items = []

    for it in items:
        tid = it.get("type_id", 0)
        qty = it.get("quantity", 1)
        info = prices.get(str(tid), {})
        unit_price = info.get("average_price", 0.0) or info.get("adjusted_price", 0.0) if isinstance(info, dict) else 0.0
        item_val = unit_price * qty
        total_value += item_val

        valued_items.append({
            **it,
            "unit_price": unit_price,
            "total_value": item_val,
        })

    valued_items.sort(key=lambda x: x["total_value"], reverse=True)

    return {
        "total_valuation": round(total_value, 2),
        "total_items": len(items),
        "top_items": valued_items[:top_k],
        "items": valued_items,
    }
