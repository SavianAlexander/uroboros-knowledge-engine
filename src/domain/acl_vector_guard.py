"""
Multi-Tenant ACL & Role Vector Isolation Guard Engine.
Filters candidate vector chunks dynamically based on user tenant ID and role permissions.
Zero-dependency, stdlib implementation.
"""
import unicodedata

from typing import List, Dict, Any


def filter_candidates_by_acl(
    candidates: List[Dict[str, Any]],
    user_tenant_id: str,
    user_roles: List[str]
) -> Dict[str, Any]:
    """
    Filters vector candidates to ensure user tenant ID and role permissions match document ACLs.
    """
    if not candidates:
        return {"allowed_candidates": [], "blocked_count": 0, "status": "success"}

    allowed = []
    blocked_count = 0
    norm_user_tenant = unicodedata.normalize("NFC", str(user_tenant_id or "default"))
    roles_set = set(unicodedata.normalize("NFC", str(r)).lower() for r in user_roles)
    # Admin roles bypass role checks
    is_admin = "admin" in roles_set or "role:admin" in roles_set

    for cand in candidates:
        raw_tenant = str(cand.get("tenant_id", "default"))
        doc_tenant = unicodedata.normalize("NFC", raw_tenant)
        doc_roles = set(unicodedata.normalize("NFC", str(r)).lower() for r in cand.get("allowed_roles", []))

        # Check Tenant Isolation
        if doc_tenant != "global" and doc_tenant != user_tenant_id:
            blocked_count += 1
            continue

        # Check Role Isolation
        if doc_roles and not is_admin and not doc_roles.intersection(roles_set):
            blocked_count += 1
            continue

        allowed.append(cand)

    return {
        "allowed_candidates": allowed,
        "blocked_count": blocked_count,
        "total_candidates": len(candidates),
        "user_tenant_id": user_tenant_id,
        "status": "success"
    }
