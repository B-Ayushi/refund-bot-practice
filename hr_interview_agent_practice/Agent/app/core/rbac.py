from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Set


@dataclass(frozen=True)
class RolePolicy:
    allowed_actions: Set[str]


class RBAC:
    """Simple RBAC engine for employee actions and data access."""

    def __init__(self) -> None:
        self.roles: Dict[str, RolePolicy] = {
            "employee": RolePolicy({
                "view_own_profile",
                "request_leave",
                "view_own_payroll",
                "request_reimbursement",
                "request_transfer",
                "generate_verification_letter",
                "submit_exit_request",
            }),
            "manager": RolePolicy({
                "view_own_profile",
                "view_team_profile",
                "approve_leave",
                "review_payroll",
                "approve_transfer",
                "request_reimbursement",
            }),
            "hr_admin": RolePolicy({
                "view_all_profiles",
                "approve_leave",
                "review_payroll",
                "approve_transfer",
                "manage_reimbursement",
                "generate_verification_letter",
                "administer_exit_process",
                "escalate_case",
            }),
        }

    def authorize(self, role: str, action: str) -> bool:
        role_policy = self.roles.get(role.lower())
        if role_policy is None:
            return False
        return action in role_policy.allowed_actions

    def can_access_employee_data(self, actor_role: str, actor_id: str, target_employee_id: str | None) -> bool:
        if target_employee_id is None:
            return True
        if actor_role.lower() == "hr_admin":
            return True
        if actor_role.lower() == "manager":
            return True
        return actor_id == target_employee_id

    def get_roles(self) -> List[str]:
        return list(self.roles.keys())
