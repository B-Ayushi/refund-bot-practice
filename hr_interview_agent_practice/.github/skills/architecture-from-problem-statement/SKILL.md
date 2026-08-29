---
name: architecture-from-problem-statement
description: "Use when: creating a technical architecture for a new agent or application from a workspace folder's problem statement; reading problemstatement.txt in a project folder; planning an AI agent system, folder structure, workflows, security, and implementation steps from business requirements; designing clean, maintainable code with no code smells."
---

# Architecture Planner from Problem Statement

## Mission

Read the problem statement in the current workspace folder, extract the real requirements, and convert them into a strong technical architecture and implementation plan for the requested AI agent or workflow system.

The output should be technically sound, secure, scalable, and maintainable, with a clean project layout and strong engineering practices.

## Inputs to Read

- problemstatement.txt in the current folder or nearest relevant project folder
- Any user-provided constraints or preferences
- Existing workspace structure if present

## Core Workflow

### 1. Read and Extract Requirements

Read the problem statement and identify:

- business goal
- user personas and actors
- user requests and workflows
- tools and external systems involved
- policy, compliance, and risk constraints
- security and privacy boundaries
- scale and latency requirements
- availability and resilience goals
- escalation and exception handling rules

### 2. Classify the Requirements

Separate the problem into clear buckets:

- Functional requirements
- Non-functional requirements
- Security and compliance requirements
- Human-in-the-loop escalation requirements
- Data and system integration needs
- Operational concerns

### 3. Decide the Architecture Pattern

Choose an architecture based on complexity:

- Use a single-agent design only for narrow, simple workflows.
- Use a multi-agent or orchestrator + specialist agent design when the problem includes policy checks, tool calls, approvals, multiple domains, safety layers, or escalations.
- Prefer a modular design with explicit boundaries between:
  - orchestration
  - policy enforcement
  - intent classification
  - execution
  - evaluation
  - observability
  - escalation

### 4. Design the End-to-End System

Define the core components:

- Frontend or user interface layer
- API or gateway layer
- Agent orchestration layer
- Domain-specific agents or task executors
- Policy and safety guardrails
- Tool adapters for internal systems
- Memory and session management
- Data access and persistence layer
- Authentication and authorization
- Observability, logging, monitoring, and tracing
- Human escalation workflows

### 5. Produce a Workflow Diagram

Write a simple step-by-step architecture flow such as:

START
↓
Input validation and PII detection
↓
Intent and context understanding
↓
Policy and authorization checks
↓
Tool execution and workflow steps
↓
Validation and evaluation
↓
Send response or escalate to human
↓
END

### 6. Define the Folder Structure

Create a clean, maintainable folder layout with bounded responsibilities.

Recommended high-quality structure:

```text
project/
├── README.md
├── .env.example
├── requirements.txt or package.json
├── pyproject.toml or tsconfig.json
├── docker-compose.yml
├── Makefile
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── routes/
│   │   ├── schemas/
│   │   └── dependencies.py
│   ├── core/
│   │   ├── config.py
│   │   ├── logging.py
│   │   ├── security.py
│   │   └── constants.py
│   ├── domain/
│   │   ├── entities/
│   │   ├── services/
│   │   └── policies/
│   ├── agents/
│   │   ├── orchestrator/
│   │   ├── intent_agent/
│   │   ├── policy_agent/
│   │   ├── execution_agent/
│   │   └── escalation_agent/
│   ├── tools/
│   │   ├── hr_tools.py
│   │   ├── payroll_tools.py
│   │   ├── leave_tools.py
│   │   └── document_tools.py
│   ├── memory/
│   │   ├── session_store.py
│   │   └── context_manager.py
│   ├── integrations/
│   │   ├── employee_db.py
│   │   ├── payroll_api.py
│   │   ├── ticketing_client.py
│   │   └── document_service.py
│   ├── workflows/
│   │   ├── leave_workflow.py
│   │   ├── payroll_workflow.py
│   │   ├── transfer_workflow.py
│   │   └── exit_workflow.py
│   └── utils/
│       ├── validators.py
│       ├── errors.py
│       └── formatting.py
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   └── fixtures/
├── infra/
│   ├── terraform/
│   ├── kubernetes/
│   └── monitoring/
├── docs/
│   ├── architecture.md
│   ├── security.md
│   └── runbook.md
└── scripts/
    ├── lint.sh
    ├── test.sh
    └── deploy.sh
```

### 7. Design for Good Code Quality and Zero Code Smells

The architecture should explicitly enforce strong engineering quality:

- clear separation of concerns
- small focused modules
- no giant classes or god functions
- no hidden side effects
- no business logic spread across layers
- dependency injection over hardcoded dependencies
- typed interfaces and schemas
- centralized error handling
- validation at boundaries
- explicit retries, timeouts, and circuit breakers
- consistent naming and layered responsibility
- no duplicate logic across workflow handlers
- no unsafe prompt execution without validation
- all sensitive action paths require authorization and audit trails

### 8. Define Security and Safety Rules

The solution must include:

- prompt injection detection
- jailbreak defense
- PII masking and redaction
- least-privilege authorization
- row-level access enforcement
- explicit approval for high-risk actions
- audit logs for all decisions and outbound actions
- sensitive-data encryption in transit and at rest
- safe handling of payroll, salaries, bank data, tax records, and employee performance information
- policy conflict escalation instead of silent override

### 9. Define the Decision Logic

For each business requirement, decide:

- which agent or service handles it
- what tools are called
- what policies are enforced
- when escalation is required
- how success is validated
- what failure states are expected

### 10. Produce the Final Deliverable

Return a structured architecture plan with these sections:

1. Executive summary
2. Business understanding from problem statement
3. Recommended architecture: single-agent vs multi-agent
4. High-level component architecture
5. Workflow diagram
6. Security and safety strategy
7. Data and integration design
8. Folder and code structure
9. Implementation phases and milestones
10. Testing strategy
11. Observability and operations plan
12. Risk analysis and mitigation
13. Code quality checklist
14. Final recommendation

## Quality Criteria

A strong result should:

- match the business problem precisely
- be grounded in the real requirements in problemstatement.txt
- show a practical system design rather than a generic template
- define agent responsibilities clearly
- include safety, compliance, and escalation paths
- propose a maintainable project structure
- emphasize clean code and engineering discipline
- avoid vague or over-abstract architecture
- explain trade-offs and why the design is chosen

## Completion Checklist

Before finalizing the architecture, confirm:

- the business problem is fully understood
- requirements are mapped to components
- system boundaries are explicit
- security requirements are addressed
- monitoring and auditability are planned
- the folder structure is clean and scalable
- code quality practices are included
- the design supports growth, performance, and supportability

## Example Prompt to Trigger This Skill

- Create the architecture for this project from problemstatement.txt.
- Read the problem statement in this folder and design the full agent system and folder structure.
- Based on the requirements in problemstatement.txt, propose a secure multi-agent architecture with clean code practices.
- Build a technical blueprint for this HR support agent, including workflow design, folder structure, and implementation plan.

## Related Customizations to Consider Next

- a README generation skill for project setup and onboarding
- a testing strategy skill for agent validation and quality gates
- a security review skill for prompt injection, authorization, and PII protection
- a project scaffolding skill that creates the folder structure automatically
- a code review skill focused on removing code smells and enforcing maintainability
