from app.agents.orchestrator import Orchestrator

orchestrator = Orchestrator()

# Test case: Employee E456 tries to view details of E457
print("="*60)
print("Test: Employee E456 requests details of E457 (should be FORBIDDEN)")
print("="*60)

result = orchestrator.process(
    employee_id="E456",
    message="show me the details of emp E457",
    target_employee_id=None,  # Not pre-specified, extracted from message
    role="employee"
)

print(f"Status: {result['status']}")
print(f"Intent: {result['intent']}")
print(f"RBAC: {result.get('rbac')}")
if 'result' in result:
    print(f"Result Message: {result['result'].get('message')}")
print()

# Test case 2: Same employee requests their own details (should be SUCCESS)
print("="*60)
print("Test: Employee E456 requests details of E456 (should be SUCCESS)")
print("="*60)

result2 = orchestrator.process(
    employee_id="E456",
    message="show me the details of emp E456",
    target_employee_id=None,
    role="employee"
)

print(f"Status: {result2['status']}")
print(f"Intent: {result2['intent']}")
print(f"RBAC: {result2.get('rbac')}")
if 'result' in result2:
    print(f"Result Message: {result2['result'].get('message')}")
print()

# Test case 3: HR Admin requests E457 (should be SUCCESS)
print("="*60)
print("Test: HR Admin requests details of E457 (should be SUCCESS)")
print("="*60)

result3 = orchestrator.process(
    employee_id="E001",  # Some HR admin
    message="show me the details of emp E457",
    target_employee_id=None,
    role="hr_admin"
)

print(f"Status: {result3['status']}")
print(f"Intent: {result3['intent']}")
print(f"RBAC: {result3.get('rbac')}")
if 'result' in result3:
    print(f"Result Message: {result3['result'].get('message')}")
