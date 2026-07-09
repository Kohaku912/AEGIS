"""Verification — post-execution outcome verification.

Ensures that tool executions actually achieved their intended outcomes
by checking real-world state after execution.
"""

from aegis_ai.verification.verification_types import (
    CompletionCondition,
    CompletionObservable,
    VerificationRequest,
    VerificationResult,
    VerificationStatus,
    VerificationStrategy,
)
from aegis_ai.verification.verifier import VerificationService

__all__ = [
    "VerificationRequest",
    "VerificationResult",
    "VerificationStatus",
    "VerificationStrategy",
    "CompletionCondition",
    "CompletionObservable",
    "VerificationService",
]
