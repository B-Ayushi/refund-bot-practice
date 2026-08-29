from dataclasses import dataclass
from typing import Dict, List


@dataclass
class LeaveRequest:
    employee_id: str
    start_date: str
    end_date: str
    leave_type: str = "casual"


class HRToolService:
    def __init__(self) -> None:
        self._employee_data: Dict[str, Dict[str, object]] = {
            "E123": {"name": "Amit Kumar", "role": "Engineer", "manager": "M001"},
            "E456": {"name": "Neha Singh", "role": "Analyst", "manager": "M002"},
        }
        self._leave_requests: List[LeaveRequest] = []

    def get_employee_details(self, employee_id: str) -> Dict[str, object]:
        return self._employee_data.get(employee_id, {"name": "Unknown", "role": "Unknown"})

    def apply_leave(self, employee_id: str, start_date: str, end_date: str, leave_type: str = "casual") -> dict:
        request = LeaveRequest(employee_id=employee_id, start_date=start_date, end_date=end_date, leave_type=leave_type)
        self._leave_requests.append(request)
        return {
            "status": "approved",
            "employee_id": employee_id,
            "start_date": start_date,
            "end_date": end_date,
            "leave_type": leave_type,
            "message": "Leave request submitted successfully.",
        }

    def get_payroll_status(self, employee_id: str) -> dict:
        return {
            "employee_id": employee_id,
            "status": "paid",
            "message": "Payroll for this cycle is processed successfully.",
        }

    def generate_verification_letter(self, employee_id: str) -> dict:
        employee = self.get_employee_details(employee_id)
        return {
            "employee_id": employee_id,
            "employee_name": employee["name"],
            "status": "generated",
            "document": "Employment verification letter created.",
        }

    def create_reimbursement_ticket(self, employee_id: str, category: str) -> dict:
        return {
            "employee_id": employee_id,
            "ticket_id": f"RT-{employee_id}-{category.upper()}",
            "status": "open",
            "message": f"Reimbursement ticket for {category} created.",
        }
