"""
Pillar 2: Privacy & Security Domain Subpackage.
Encapsulates zero-knowledge data masking, PII scrubbing, cryptographic audit hashchains,
Merkle trees, ACL permissions, client dataset cleaning, and verification invariants.
"""
from src.domain.zk_data_masker import (
    pseudonymize_records,
    mask_pii_entities,
    ZkDataMasker,
)
from src.domain.pii_privacy_guard import (
    redact_pii_from_text,
    inspect_and_redact_pii,
    PiiPrivacyGuard,
)
from src.domain.privacy_anonymizer import (
    anonymize_sensitive_payload,
    PrivacyAnonymizer,
)
from src.domain.audit_hashchain import (
    AuditHashChain,
    record_audit_event,
    verify_hashchain_integrity,
)
from src.domain.crypto_audit_ledger import CryptoAuditLedger
from src.domain.vault_merkle_tree import VaultMerkleTree
from src.domain.acl_permission_engine import AclPermissionEngine
from src.domain.acl_vector_guard import AclVectorGuard
from src.domain.compliance_inspector import ComplianceInspector
from src.domain.prompt_injection_guard import PromptInjectionGuard, evaluate_prompt_safety
from src.domain.data_provenance_tracker import DataProvenanceTracker
from src.domain.client_data_cleaner import cleanse_client_dataset
from src.domain.boundary_invariants import evaluate_boundary_invariants
from src.domain.verification_guards import verify_claims_and_consensus

__all__ = [
    "pseudonymize_records",
    "mask_pii_entities",
    "ZkDataMasker",
    "redact_pii_from_text",
    "inspect_and_redact_pii",
    "PiiPrivacyGuard",
    "anonymize_sensitive_payload",
    "PrivacyAnonymizer",
    "AuditHashChain",
    "record_audit_event",
    "verify_hashchain_integrity",
    "CryptoAuditLedger",
    "VaultMerkleTree",
    "AclPermissionEngine",
    "AclVectorGuard",
    "ComplianceInspector",
    "PromptInjectionGuard",
    "evaluate_prompt_safety",
    "DataProvenanceTracker",
    "cleanse_client_dataset",
    "evaluate_boundary_invariants",
    "verify_claims_and_consensus",
]
