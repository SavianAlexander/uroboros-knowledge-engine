"""
Zero-dependency Enterprise ACL Permission & Security Trimming Engine.
Evaluates user identities, group memberships, and clearance levels against document security labels.
Mimics Microsoft Entra ID (Active Directory) security trimming.
"""

from typing import Dict, Any, List, Set


def is_user_authorized(
    user_context: Dict[str, Any],
    document_acl: Dict[str, Any]
) -> bool:
    """
    Evaluates if user_context (user_id, roles/groups, clearance_level) is authorized to access document_acl.
    Zero-dependency stdlib implementation.
    """
    if not user_context or not isinstance(user_context, dict):
        return False
    if not document_acl or not isinstance(document_acl, dict):
        return True  # Public document

    # 1. Check direct owner access
    user_id = user_context.get("user_id")
    owner_id = document_acl.get("owner_id")
    if owner_id and user_id and str(user_id) == str(owner_id):
        return True

    # 2. Check clearance level requirement
    raw_req = document_acl.get("clearance_level", 0)
    raw_user = user_context.get("clearance_level", 0)
    req_clearance = int(raw_req) if raw_req is not None and isinstance(raw_req, (int, float, str)) and str(raw_req).isdigit() else 0
    user_clearance = int(raw_user) if raw_user is not None and isinstance(raw_user, (int, float, str)) and str(raw_user).isdigit() else 0
    if user_clearance < req_clearance:
        return False

    # 3. Check allowed roles/groups (Active Directory / Entra ID Security Groups)
    import unicodedata
    allowed_roles = set(unicodedata.normalize("NFC", str(r)) for r in document_acl.get("read_roles", []))
    if not allowed_roles or "*" in allowed_roles:
        return True  # Open to all authenticated users

    user_roles = set(unicodedata.normalize("NFC", str(r)) for r in user_context.get("roles", []))
    user_groups = set(unicodedata.normalize("NFC", str(g)) for g in user_context.get("groups", []))
    user_principal = user_roles.union(user_groups)

    return len(allowed_roles.intersection(user_principal)) > 0


def trim_search_results_by_acl(
    user_context: Dict[str, Any],
    results: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Trims search results based on user identity & Active Directory group memberships.
    """
    authorized_results = []
    for r in results:
        doc_acl = r.get("acl") or {
            "read_roles": r.get("read_roles", []),
            "owner_id": r.get("owner_id"),
            "clearance_level": r.get("clearance_level", 0)
        }

        if is_user_authorized(user_context, doc_acl):
            authorized_results.append(r)

    return authorized_results
