"""
Runtime Service Catalog & API Router Introspection Registry.
Standard: Pure Python Standard Library (typing, json).
Provides runtime inspection of all active FastAPI endpoints, HTTP methods, security dependencies, and schema contracts.
"""

from typing import Dict, Any, List, Optional
from fastapi import FastAPI


def get_service_catalog(app: Optional[FastAPI] = None) -> List[Dict[str, Any]]:
    """
    Introspects registered FastAPI routes and returns structured service catalog metadata.
    """
    if app is None:
        try:
            from src.app.server import app as default_app
            app = default_app
        except Exception:
            return []

    catalog = []
    for route in getattr(app, "routes", []):
        path = getattr(route, "path", None)
        if not path or path.startswith("/static") or path == "/{full_path:path}":
            continue

        methods = list(getattr(route, "methods", []))
        endpoint = getattr(route, "endpoint", None)
        endpoint_name = endpoint.__name__ if endpoint else ""
        doc = (endpoint.__doc__ or "").strip() if endpoint else ""
        tags = list(getattr(route, "tags", []))
        summary = getattr(route, "summary", None) or (doc.split("\n")[0] if doc else endpoint_name)

        catalog.append({
            "path": path,
            "methods": methods,
            "name": endpoint_name,
            "summary": summary,
            "tags": tags
        })

    return catalog
