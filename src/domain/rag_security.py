"""
Multi-Tenant RBAC Security Pre-Filtering & Authentication Context Module.
Provides deterministic role-based and tenant-level isolation for vector and lexical retrieval layers.
"""

import json
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple, Set


@dataclass
class AuthContext:
    """Security context representing the authenticated caller."""
    tenant_id: str = "default"
    user_id: str = "anonymous"
    roles: List[str] = field(default_factory=lambda: ["user"])
    max_classification: str = "internal"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "roles": list(self.roles),
            "max_classification": self.max_classification
        }

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "AuthContext":
        if not data:
            return cls()
        return cls(
            tenant_id=data.get("tenant_id", "default"),
            user_id=str(data.get("user_id", "anonymous")),
            roles=data.get("roles") or data.get("user_roles") or ["user"],
            max_classification=data.get("max_classification", "internal")
        )


class RBACFilterBuilder:
    """Constructs database and in-memory pre-filters for multi-tenant isolation."""

    @staticmethod
    def build_sql_filter(auth: Optional[AuthContext], prefix: str = "f") -> Tuple[str, List[Any]]:
        """
        Builds SQL WHERE clause and parameter list enforcing tenant and role isolation.
        """
        if not auth:
            return "", []

        p = f"{prefix}." if prefix else ""
        clauses = []
        params = []

        # 1. Tenant Isolation
        clauses.append(f"({p}tenant_id = ? OR {p}tenant_id = '*' OR {p}tenant_id IS NULL)")
        params.append(auth.tenant_id)

        # 2. Role-based Access Control
        role_conditions = [f"{p}allowed_roles LIKE '%\"*\"%'", f"{p}allowed_roles IS NULL"]
        for role in auth.roles:
            role_conditions.append(f"{p}allowed_roles LIKE ?")
            params.append(f'%"{role}"%')
        clauses.append(f"({' OR '.join(role_conditions)})")

        # 3. User ACL
        user_conditions = [
            f"{p}user_acl LIKE '%\"*\"%'",
            f"{p}user_acl IS NULL",
            f"{p}user_acl LIKE ?"
        ]
        params.append(f'%"{auth.user_id}"%')
        clauses.append(f"({' OR '.join(user_conditions)})")

        return " AND ".join(clauses), params

    @staticmethod
    def build_vector_prefilter(auth: Optional[AuthContext]) -> Dict[str, Any]:
        """
        Builds standard vector DB pre-filter specification (e.g., Qdrant / Elasticsearch schema).
        """
        if not auth:
            return {}

        roles_allowed = list(set(auth.roles + ["*"]))
        user_acls = list(set([auth.user_id, "*"]))

        return {
            "must": [
                {
                    "key": "tenant_id",
                    "match": {"value": auth.tenant_id}
                },
                {
                    "key": "allowed_roles",
                    "match": {"any": roles_allowed}
                },
                {
                    "key": "user_acl",
                    "match": {"any": user_acls}
                }
            ]
        }

    @staticmethod
    def matches_auth(item: Dict[str, Any], auth: Optional[AuthContext]) -> bool:
        """
        In-memory fast filter matching for vector matrices and candidate chunk lists.
        Returns True if item is accessible to the auth context, False otherwise.
        """
        if not auth:
            return True

        # 1. Tenant Check
        item_tenant = item.get("tenant_id") or "default"
        if item_tenant != "*" and item_tenant != auth.tenant_id:
            return False

        # 2. Role Check
        allowed_roles = item.get("allowed_roles")
        if isinstance(allowed_roles, str):
            try:
                allowed_roles = json.loads(allowed_roles)
            except Exception:
                allowed_roles = [allowed_roles]
        if not allowed_roles:
            allowed_roles = ["*"]

        if "*" not in allowed_roles:
            user_roles_set = set(auth.roles)
            if not any(r in user_roles_set for r in allowed_roles):
                return False

        # 3. User ACL Check
        user_acl = item.get("user_acl")
        if isinstance(user_acl, str):
            try:
                user_acl = json.loads(user_acl)
            except Exception:
                user_acl = [user_acl]
        if not user_acl:
            user_acl = ["*"]

        if "*" not in user_acl:
            if str(auth.user_id) not in [str(u) for u in user_acl]:
                return False

        return True
