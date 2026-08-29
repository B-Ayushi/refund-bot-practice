from __future__ import annotations

import re
from typing import Dict, Optional


class IntentAgent:
    def detect_intent(self, message: str) -> str:
        lower = message.lower()

        if "leave" in lower:
            return "apply_leave"
        if "salary" in lower or "payroll" in lower:
            return "check_payroll_status"
        if "reimbursement" in lower or "claim" in lower:
            return "create_reimbursement_ticket"
        if "verification" in lower or "employment letter" in lower:
            return "generate_verification_letter"
        if "transfer" in lower:
            return "transfer_request"
        if "resign" in lower or "exit" in lower:
            return "exit_request"
        return "unknown"

    def extract_dates(self, message: str) -> Optional[Dict[str, str]]:
        matches = re.findall(r"\b(?:next|this)\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", message.lower())
        if matches:
            return {"start_date": "next-selected-day", "end_date": "next-selected-day"}
        return None
