# HR Agent Architecture with LLM Reasoning, MCP Routing, and Istio

## Overview

This architecture adds three critical layers to the base HR support agent:

1. LLM reasoning layer for smarter intent classification and context extraction
2. MCP-style model routing layer to assign small models to simple tasks and large models to complex tasks
3. Istio-based service mesh pattern for traffic management, load balancing, and routing across model and service endpoints

## 1. Reasoning layer

The reasoning layer sits above the traditional intent classifier and performs:

- intent classification using LLM-style reasoning
- extraction of context and ambiguity signals
- risk scoring
- route selection before workflow execution

This improves accuracy for natural language requests such as:

- "I need to apply leave tomorrow"
- "My salary credit is incorrect"
- "I want to resign and ask for exit support"

## 2. MCP model routing layer

The model routing layer chooses the model size based on task complexity and risk:

- small model for standard tasks
  - simple leave requests
  - informational HR queries
  - basic status checks
- large model for complex or high-risk tasks
  - policy conflicts
  - payroll disputes
  - termination or legal-sensitive cases
  - ambiguous multi-step workflows

Conceptually:

```text
User request
   -> safety guardrail
   -> reasoning layer
   -> MCP router
   -> small model or large model
   -> execution + policy enforcement
   -> escalate if needed
```

## 3. Istio integration concept

Istio is used at the service mesh layer to manage traffic across:

- API gateway
- agent services
- model inference endpoints
- policy and escalation services
- internal HR integrations

Key features:

- traffic splitting between small and large model endpoints
- A/B or weighted routing for model versions
- circuit breakers and retries
- rate limiting and request shaping
- observability and tracing
- service-level resilience and load balancing

## Example traffic routing policy

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: hr-agent-routing
spec:
  hosts:
    - hr-agent.internal
  http:
    - match:
        - headers:
            x-model-tier:
              exact: small
      route:
        - destination:
            host: small-model-service
            port:
              number: 8080
    - route:
        - destination:
            host: large-model-service
            port:
              number: 8080
```

## Recommended deployment pattern

```text
Internet / Employee App
        |
        v
API Gateway
        |
        v
Istio Service Mesh
   |-- small-model-service
   |-- large-model-service
   |-- orchestrator-service
   |-- policy-service
   |-- escalation-service
   |-- hr-system-integration-layer
```

## Why this is the right pattern

This design gives you:

- smarter interpretation of employee intent
- better response quality by using the right model for the task
- safer handling of high-risk HR decisions
- easier scaling and load balancing through Istio
- clearer operational control for service traffic and resilience
