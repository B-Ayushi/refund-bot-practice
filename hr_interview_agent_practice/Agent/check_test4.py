from app.agents.reasoning_agent import ReasoningAgent

r = ReasoningAgent()

msg = 'show me the details of emp E456'
print(f'Message: {msg}')
print(f'Is deterministic: {r.is_deterministic_request(msg)}')

sec = r.security_check_via_groq(msg)
print(f'Security: is_malicious={sec.get("is_malicious")}, threat={sec.get("threat_level")}')
print(f'Reason: {sec.get("reason")}')
