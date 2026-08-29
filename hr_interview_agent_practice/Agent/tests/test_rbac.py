from app.core.rbac import RBAC


def test_employee_can_access_own_profile():
    rbac = RBAC()
    assert rbac.authorize("employee", "request_leave") is True
    assert rbac.can_access_employee_data("employee", "E123", "E123") is True


def test_employee_cannot_access_other_profile():
    rbac = RBAC()
    assert rbac.can_access_employee_data("employee", "E123", "E456") is False


def test_hr_admin_has_full_access():
    rbac = RBAC()
    assert rbac.authorize("hr_admin", "escalate_case") is True
    assert rbac.can_access_employee_data("hr_admin", "HR1", "E456") is True
