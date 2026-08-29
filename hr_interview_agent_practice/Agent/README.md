# HR Support Agent

This is a proof-of-concept implementation of an AI-powered HR support agent based on the provided business requirements.

## Features

- natural-language request handling for common HR workflows
- policy-aware agent decision flow
- blocked sensitive actions for unauthorized access
- escalation path for high-risk scenarios
- modular folder structure for maintainability

## Run

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Example

POST to `/chat` with a JSON body such as:

```json
{
  "employee_id": "E123",
  "message": "I want to apply for casual leave next Monday and Tuesday"
}
```

## Notes

This is intentionally structured as a clean starter project and not a full enterprise system.
