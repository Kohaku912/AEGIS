"""Service Permission Scopes — fine-grained access control for external services."""

from aegis_ai.permissions.service_permission_policy import (
    ServicePermissionPolicy,
    infer_service_operation_from_browser_action,
)
from aegis_ai.permissions.service_permission_store import PermissionDecision, ServicePermissionStore
from aegis_ai.permissions.service_scope_types import (
    OAuthScopeMapping,
    Operation,
    OperationCategory,
    Service,
    ServicePermissionScope,
    get_operation_category,
    infer_operation_from_element,
    infer_service_from_url,
)

__all__ = [
    "OAuthScopeMapping",
    "Operation",
    "OperationCategory",
    "PermissionDecision",
    "Service",
    "ServicePermissionPolicy",
    "ServicePermissionScope",
    "ServicePermissionStore",
    "get_operation_category",
    "infer_operation_from_element",
    "infer_service_from_url",
    "infer_service_operation_from_browser_action",
]
