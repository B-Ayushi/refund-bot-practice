# Intelligent Travel Planner

## System Goal

Build a production-grade AI travel planning system that converts a user's natural-language travel request into a safe, feasible, personalized, and reviewable itinerary.

The system must:

- Understand explicit and implicit travel requirements.
- Preserve uncertainty instead of inventing missing values.
- Respect budget, duration, weather, policy, safety, and user preferences.
- Use external tools for factual travel data.
- Produce a complete day-by-day itinerary with traceable assumptions.
- Use session memory to personalize future requests.
- Communicate between components only through validated structured JSON.

The system must not present unverified facts as certain. Prices, availability, weather, travel times, opening hours, and policy-sensitive information must be marked with their source time and confidence, or explicitly identified as estimates.

## Scope and Non-Goals

In scope:

- Destination discovery when the user has not selected a destination.
- Destination feasibility validation.
- Hotel and attraction discovery.
- Weather-aware itinerary planning.
- Budget allocation and validation.
- Conversational clarification when required.
- Session-level personalization and preference memory.

Out of scope unless separately integrated:

- Booking, payment, cancellation, or reservation execution.
- Issuing visas, permits, medical advice, or legal advice.
- Guaranteeing safety, availability, prices, weather, or transportation.
- Replacing official government, airline, hotel, or emergency guidance.

## Architectural Principles

1. **No Intent Agent.** Use a lightweight LLM Extraction Layer only for normalization. It must not recommend destinations or make planning decisions.
2. **Deterministic orchestration.** The Validation Loop Agent owns state transitions and termination. LLMs do not decide whether the workflow terminates.
3. **Structured communication.** Every agent input and output is JSON validated against a versioned schema. No free-form agent-to-agent messages are permitted.
4. **Evidence before synthesis.** Planning agents may use only user data, memory, validated tool results, and explicitly approved assumptions.
5. **Fail closed for safety and policy.** Policy or guardrail failure terminates the workflow immediately.
6. **Human control for weather warnings.** A warning informs the user and pauses for an explicit choice; it does not silently override the user's destination.
7. **Bounded loops.** Every loop has a maximum iteration count, timeout, and resumable state.
8. **Least privilege.** Each agent receives only the fields and tools required for its responsibility.
9. **Reproducibility.** Persist request, schema versions, tool snapshots, decisions, and correlation identifiers.
10. **Contract Completeness.** No downstream agent is allowed to execute on an incomplete `TravelRequest`. The Travel Request Understanding Layer owns extraction, validation, and clarification before workflow execution begins. Only schema-complete requests may proceed to Input Guardrails, the Validation Loop Agent, Policy Agent, Guardrail Agent, Weather Agent, Hotel Agent, Attraction Agent, Itinerary Agent, or Reviewer Agent.

## Architecture

```text
User Request
  |
  v
Travel Request Understanding Layer
  |
  +--> LLM Extraction Layer
  |          |
  |          v
  +--> Schema Validation Layer
         |
      Complete?
      |       |
       No      Yes
      |       |
      v       v
   Clarification Loop  Complete TravelRequest
      |                 |
      +-----------------+
                |
                v
Stage 1: Input Guardrails
    | fail -> Generic rejection and terminal state
    v
Validation Loop Agent
    |
    +--> Policy Agent --------+
    +--> Guardrail Agent -----+--> Gather and deterministic decision
    +--> Weather Agent -------+
                                  |
       warning -> Human-in-the-loop decision and loop continuation
       pass    -> Planning workflow
       fail    -> Generic rejection and terminal state

Planning Workflow
    |
    +--> Hotel Agent ---------+
    +--> Attraction Agent ----+--> Gather
                                  |
                                  v
                           Itinerary Agent
                                  |
                                  v
                           Reviewer Agent
                           |             |
                      approve       revision request
                           |             |
                       Final Plan <-----+
```

Hotel and Attraction Agents are independent and should run in parallel after validation succeeds. The Itinerary Agent runs after their results are gathered. The Reviewer Agent is the final quality gate.

## Workflow Pattern

### Request Lifecycle

Each request is represented by a durable workflow state with a unique `request_id`, `session_id`, `workflow_version`, and `correlation_id`.

The Travel Request Understanding Layer must complete extraction, schema validation, and clarification before the request can enter Input Guardrails, the Validation Loop Agent, validation agents, or the planning workflow. A request cannot enter validation or planning until the `TravelRequest` contract is complete.

Allowed terminal states:

- `completed`: reviewer approved a final itinerary.
- `rejected_policy`: policy agent failed.
- `rejected_guardrail`: guardrail agent failed.
- `needs_user_input`: explicit clarification or weather decision is required.
- `failed_recoverable`: transient infrastructure failure exhausted local retries; safe resume is possible.
- `failed_terminal`: required data could not be obtained or the workflow exceeded its safety limits.
- `cancelled`: user or operator cancelled the request.

### Stage 0: Travel Request Understanding Layer

The Travel Request Understanding Layer contains:

1. LLM Extraction Layer
2. Schema Validation Layer
3. Clarification Loop

Its responsibility is to guarantee a complete `TravelRequest` contract before any downstream workflow execution.

#### LLM Extraction Layer

Responsibilities:

- Parse natural language into the normalized travel request schema.
- Extract destination, dates or duration, budget, party size, origin, trip type, constraints, preferences, and urgency when stated.
- Resolve ordinary language such as "around a week" into an explicit bounded range.
- Preserve ambiguity with `null`, ranges, and `assumptions`.
- Identify fields requiring clarification.
- Return schema-compliant JSON only.

The layer must not:

- Recommend destinations.
- Search tools.
- Claim current prices, weather, availability, or attractions.
- Infer sensitive personal attributes.
- Silently choose between materially different interpretations.

For example, "somewhere for around a week and budget-friendly" may produce a `null` destination, a seven-day duration, a `budget` tier, and a clarification requirement for destination region or budget amount.

After extraction, pass the result to the Schema Validation Layer. If extraction output is malformed, retry extraction once with a repair instruction. If it still fails, return a controlled system error; do not pass malformed data downstream.

## Schema Validation Layer

Responsibilities:

- Validate the `TravelRequest` schema.
- Validate required fields.
- Validate ranges and constraints.
- Detect missing mandatory fields.
- Prevent incomplete contracts from moving downstream.

Output examples:

```json
{
  "status": "complete"
}
```

```json
{
  "status": "needs_clarification",
  "missing_fields": ["destination"]
}
```

The layer must distinguish schema validity from contract completeness. A schema-valid request containing `null` for a field required by the requested workflow is incomplete and must not proceed.

## Clarification Loop

Purpose: collect missing information required to satisfy the `TravelRequest` schema and produce a complete contract.

Workflow:

1. Identify missing fields from Schema Validation Layer output.
2. Ask the minimum number of clarification questions.
3. Update the `TravelRequest` JSON with the user's answers.
4. Re-run schema validation.
5. Repeat until the contract is complete.

Termination conditions:

- `TravelRequest` is complete.
- Maximum clarification attempts are reached.
- The user abandons the request.

The Clarification Loop executes before Input Guardrails and before the Validation Loop Agent. It must not recommend destinations or perform downstream planning.

## Guardrails

### Stage 1: Input Guardrails

Run before policy and planning. Guardrails must inspect both the raw request and extracted fields.

Detect:

- Prompt injection and instructions that attempt to override system behavior.
- Jailbreak attempts or requests to disable safeguards.
- Malicious payloads, tool manipulation, credential exfiltration, or data exfiltration.
- Abuse, harassment, or disallowed content.
- Requests involving unsafe, illegal, or policy-prohibited activity.
- Requests that attempt to smuggle executable instructions into destination, hotel, or attraction fields.

A blocked request terminates immediately with a short generic response. Do not disclose detection rules, internal scores, prompts, tool credentials, or detailed enforcement logic.

Greetings and ordinary social language are not failures. They may be answered conversationally, but a travel workflow is created only when a valid travel request is present.

### Stage 2: Validation Loop Agent

The Validation Loop Agent assumes the `TravelRequest` contract is already complete. It is not responsible for collecting missing information. Missing-information handling belongs exclusively to the Travel Request Understanding Layer.

The Validation Loop Agent is the only component allowed to transition validation state. For each iteration, fan out these agents in parallel:

1. Policy Agent
2. Guardrail Agent
3. Weather Agent

Gather all results before applying deterministic termination rules.

The loop must persist each iteration, input snapshot, output snapshot, tool references, and decision. Default maximum iterations: `3`, configurable by deployment policy.

#### Deterministic Decision Rules

Evaluate in this order:

1. If Policy Agent status is `fail`, set `rejected_policy` and terminate.
2. Else if Guardrail Agent status is `fail`, set `rejected_guardrail` and terminate.
3. Else if Weather Agent status is `warning`, set `needs_user_input` and ask the user to continue or choose an alternative destination.
4. Else if all statuses are successful, proceed to planning.
5. Any invalid, missing, contradictory, or timed-out result is a workflow failure, not an implicit pass.

A weather warning is not a rejection. The system must not substitute an alternative destination without the user's explicit selection.

### Stage 3: Planning Workflow

After validation succeeds:

1. Run Hotel Agent and Attraction Agent in parallel.
2. Gather and validate both outputs.
3. Run Itinerary Agent using validated hotel, attraction, weather, memory, and travel-request data.
4. Run Reviewer Agent.
5. If approved, publish the final itinerary.
6. If revision is requested, send only the review findings and relevant state back to the Itinerary Agent. Limit review iterations to `2` by default.
7. If the reviewer still cannot approve, return a transparent, recoverable failure or ask the user for the missing decision.

## Agent Definitions

### LLM Extraction Layer

Purpose: normalize user language.

Inputs: raw user message, optional session memory summary, schema version.

Outputs: `TravelRequest`.

Tools: none.

### Policy Agent

Purpose: determine whether the request is permitted under configured safety and content policy.

Inputs: normalized travel request, relevant raw text excerpts, policy version.

Outputs: `PolicyResult`.

Tools: none unless a deployment-specific policy service is configured.

Rules:

- Return `fail` for a prohibited request.
- Return a concise user-safe reason code and internal reason details separately.
- Never recommend a workaround for a prohibited request.

### Guardrail Agent

Purpose: detect prompt manipulation, malicious intent, unsafe tool-use intent, abuse, and suspicious field content.

Inputs: raw request, normalized request, extraction metadata.

Outputs: `GuardrailResult`.

Tools: none.

Rules:

- `risk_score` is an internal signal, not a user-facing explanation.
- Do not expose classifier thresholds.
- A high-risk or invalid result must fail closed.

### Weather Agent

Purpose: assess destination conditions for the requested travel window and identify material risks.

Inputs: destination, travel dates or duration, origin if relevant, trip type, weather policy thresholds.

Preconditions:

- `TravelRequest` is schema complete.
- Destination exists.
- A travel window exists or has been clarified.

Outputs: `WeatherResult`.

Tools: Weather Tool.

Rules:

- Use forecast data when available; use historical or seasonal data only when explicitly labeled.
- Return `warning` for material conditions that could affect safety or the stated trip type.
- If weather information is unavailable, return a weather/tool failure or degraded result. This is not a request-completeness issue.
- Alternative destinations must be evidence-based and must not silently replace the user's selection.

### Hotel Agent

Purpose: find accommodation options consistent with the request.

Inputs: destination, dates or duration, party size, budget, hotel preferences, accessibility needs when voluntarily provided, memory constraints.

Preconditions:

- `TravelRequest` is complete.
- Destination is available.
- Budget constraints are available.

Outputs: `HotelSearchResult`.

Tools: Hotel Search Tool.

Rules:

- Return quoted or observed prices with currency, timestamp, occupancy assumptions, and inclusions.
- Distinguish search results from availability guarantees.
- Exclude destinations or hotel categories explicitly stored as avoided preferences unless the user overrides them.

### Attraction Agent

Purpose: find suitable attractions and activities.

Inputs: destination, dates or duration, budget, trip type, interests, mobility constraints when voluntarily provided, weather result, memory constraints.

Preconditions:

- `TravelRequest` is complete.
- Destination is available.
- Trip duration is available.

Outputs: `AttractionSearchResult`.

Tools: Attraction Search Tool.

Rules:

- Include estimated duration, cost, operating constraints, source time, and weather sensitivity.
- Avoid duplicating incompatible activities or activities rejected in session memory.
- Do not invent opening hours or admission prices.

### Itinerary Agent

Purpose: compose the complete day-by-day plan from validated evidence.

Inputs: travel request, weather result, hotel result, attraction result, session memory, approved assumptions, budget policy.

Outputs: `ItineraryDraft`.

Rules:

- Include exactly the requested number of days when duration is fixed.
- Clearly label free time, travel time, meal time, and optional activities.
- Avoid overbooking and account for realistic transfer time.
- Allocate estimated costs and show the calculation.
- Mark unavailable or unverified details as estimates or alternatives.
- Never claim a booking was made.

### Reviewer Agent

Purpose: perform a final consistency, safety, completeness, and schema review.

Inputs: travel request, all evidence references, itinerary draft, validation outputs, review policy.

Outputs: `ReviewResult`.

Checks:

- Every requested day exists exactly once.
- Budget total is within the user's maximum, or variance is explicitly explained and approval is requested.
- Weather was evaluated for the destination and travel window.
- Safety and policy results passed.
- Activities match preferences and do not violate memory exclusions.
- Prices and factual claims have evidence or are labeled estimates.
- No schema violations, fabricated bookings, contradictory dates, or impossible travel times exist.
- Required assumptions and unresolved uncertainties are visible.

## Input Contracts

### TravelRequest

```json
{
  "schema_version": "travel_request.v1",
  "destination": {
    "name": null,
    "country": null,
    "confidence": 0.0,
    "user_provided": false
  },
  "origin": null,
  "dates": {
    "start": null,
    "end": null,
    "timezone": null
  },
  "days": {
    "min": 7,
    "max": 7
  },
  "party": {
    "adults": 1,
    "children": 0
  },
  "budget": {
    "currency": "INR",
    "min": null,
    "max": null,
    "tier": "budget",
    "includes": ["accommodation", "food", "activities", "local_transport"]
  },
  "trip_type": "relaxation",
  "interests": [],
  "constraints": [],
  "preferences": {},
  "clarifications_required": ["destination", "budget.max"],
  "assumptions": [],
  "extraction_confidence": 0.0
}
```

Required invariants:

- `days.min` and `days.max` are positive integers and `min <= max`.
- `budget.min` and `budget.max`, when present, are non-negative and use the declared currency.
- Dates must be ISO 8601 calendar dates and `start <= end`.
- A fixed date range and fixed day count must agree, allowing a configured travel-day convention.
- Unknown values are `null`; they must not be replaced with fabricated defaults.
- `clarifications_required` must be populated when a required planning decision cannot be made safely.

## Output Contracts

All outputs include `schema_version`, `request_id`, `agent`, `status`, `created_at`, and `evidence_refs` where applicable.

### PolicyResult

```json
{
  "schema_version": "policy_result.v1",
  "agent": "policy",
  "status": "pass",
  "reason_code": null,
  "user_message": null,
  "internal_reason": null,
  "evidence_refs": []
}
```

`status` is `pass` or `fail`. `user_message` must be generic and safe when failure occurs.

### GuardrailResult

```json
{
  "schema_version": "guardrail_result.v1",
  "agent": "guardrail",
  "status": "pass",
  "risk_score": 0.0,
  "signals": [],
  "user_message": null,
  "evidence_refs": []
}
```

`status` is `pass` or `fail`; `risk_score` is between `0.0` and `1.0`.

### WeatherResult

```json
{
  "schema_version": "weather_result.v1",
  "agent": "weather",
  "status": "pass",
  "destination": "Goa, India",
  "travel_window": {
    "start": null,
    "end": null
  },
  "weather_summary": "",
  "risk_factors": [],
  "alternative_destinations": [],
  "source_timestamp": null,
  "confidence": 0.0,
  "evidence_refs": []
}
```

`status` is `pass`, `warning`, or `degraded`. `degraded` indicates a weather or provider-data issue after the complete request has been accepted; it must never indicate missing request fields. `alternative_destinations` contains structured destination suggestions with reasons and evidence, never bare names only.

### HotelSearchResult

```json
{
  "schema_version": "hotel_search_result.v1",
  "agent": "hotel",
  "status": "success",
  "destination": "Goa, India",
  "currency": "INR",
  "options": [
    {
      "name": "",
      "category": "3_star",
      "area": "",
      "nightly_price": null,
      "total_price": null,
      "taxes_included": null,
      "availability_status": "observed",
      "assumptions": [],
      "source_timestamp": null,
      "evidence_ref": ""
    }
  ],
  "limitations": [],
  "evidence_refs": []
}
```

### AttractionSearchResult

```json
{
  "schema_version": "attraction_search_result.v1",
  "agent": "attraction",
  "status": "success",
  "destination": "Goa, India",
  "options": [
    {
      "name": "",
      "category": "",
      "estimated_duration_hours": null,
      "estimated_cost": null,
      "currency": "INR",
      "weather_sensitivity": "low",
      "opening_constraints": [],
      "evidence_ref": ""
    }
  ],
  "limitations": [],
  "evidence_refs": []
}
```

### ItineraryDraft

```json
{
  "schema_version": "itinerary_draft.v1",
  "agent": "itinerary",
  "status": "draft",
  "destination": "",
  "days": [
    {
      "day": 1,
      "date": null,
      "items": [
        {
          "start_time": null,
          "end_time": null,
          "type": "activity",
          "name": "",
          "location": "",
          "estimated_cost": 0,
          "currency": "INR",
          "travel_time_minutes": 0,
          "optional": false,
          "evidence_refs": []
        }
      ],
      "day_estimated_cost": 0
    }
  ],
  "budget_breakdown": {
    "accommodation": 0,
    "food": 0,
    "activities": 0,
    "local_transport": 0,
    "contingency": 0,
    "total": 0,
    "currency": "INR",
    "calculation_assumptions": []
  },
  "assumptions": [],
  "unresolved_items": [],
  "evidence_refs": []
}
```

### ReviewResult

```json
{
  "schema_version": "review_result.v1",
  "agent": "reviewer",
  "status": "approve",
  "findings": [],
  "budget_check": {
    "status": "pass",
    "estimated_total": 0,
    "currency": "INR",
    "maximum": null
  },
  "completeness_check": {
    "status": "pass",
    "missing_days": []
  },
  "revision_instructions": [],
  "evidence_refs": []
}
```

`status` is `approve` or `request_revision`. A reviewer may not approve an invalid or incomplete schema.

## State Management

Persist the following state after every stage:

```json
{
  "request_id": "",
  "session_id": "",
  "correlation_id": "",
  "workflow_version": "",
  "current_stage": "",
  "status": "",
  "iteration": 0,
  "travel_request": {},
  "validation": {
    "policy": null,
    "guardrail": null,
    "weather": null
  },
  "planning": {
    "hotel": null,
    "attractions": null,
    "itinerary": null,
    "review": null
  },
  "pending_user_action": null,
  "memory_snapshot_id": null,
  "tool_call_refs": [],
  "assumptions": [],
  "errors": []
}
```

State requirements:

- Use idempotency keys for stage execution and tool calls.
- Make state writes atomic or transactionally recoverable.
- Never overwrite the original user request or raw tool response.
- Redact secrets and unnecessary personal data before persistence.
- Support resume after process, network, or provider failure.
- Reject stale user responses that do not match the current `pending_user_action`.

## Memory

Support session memory with explicit provenance, confidence, scope, and user control. Memory is context, not an unquestionable fact.

Example memory record:

```json
{
  "schema_version": "memory_record.v1",
  "session_id": "",
  "key": "preferences.avoid",
  "value": ["beaches"],
  "source": "user_explicit",
  "confidence": 1.0,
  "created_at": "",
  "updated_at": "",
  "expires_at": null,
  "user_editable": true
}
```

Store only information needed for travel personalization, such as:

- Preferred hotel category.
- Preferred trip type.
- Budget tier or recurring budget preference.
- Preferred pace, interests, and accessibility requirements when voluntarily provided.
- Previously rejected destinations or activities, with the reason when available.
- Explicit exclusions such as "I don't want beaches."

Rules:

- Explicit current-request instructions override memory.
- Explicit user preferences override inferred preferences.
- Do not store sensitive attributes or infer them from travel choices.
- Do not treat one-time rejection as a permanent prohibition unless the user says so; store scope and expiry.
- Show a concise personalization note when memory materially changes the plan.
- Provide commands or UI actions to inspect, correct, forget, or disable memory.
- Apply memory before attraction and hotel selection, and re-check it during review.

## Human-in-the-Loop Logic

### Clarification

Ask for clarification when a missing field materially changes safety, feasibility, or cost. Ask the smallest number of questions possible. Group independent questions in one response.

Typical required fields:

- Destination or acceptable region when no destination can be selected safely.
- Budget amount or currency when cost limits are essential.
- Duration or dates.
- Party size when accommodation or transport estimates depend on it.

### Weather Warning

When Weather Agent returns `warning`, present:

- Destination and travel window.
- Plain-language weather summary.
- Material travel or safety risks.
- Alternative destinations, if available.
- Two explicit actions: continue with the current destination or choose an alternative.

Do not proceed until the user's response is captured as a structured decision:

```json
{
  "schema_version": "weather_decision.v1",
  "action": "continue" ,
  "destination": "Goa, India",
  "warning_acknowledged": true
}
```

For `choose_alternative`, update only the destination fields and preserve the remaining request unless the user changes them. Re-run the full validation loop for the changed destination.

## Tool Definitions

All tools are adapters behind a provider-neutral interface. Tool responses must include provider, request parameters, retrieval time, source identifiers, normalized data, and an error object when unsuccessful.

### Weather Tool

Operation: `get_weather`

Input:

```json
{
  "destination": "Goa, India",
  "start_date": null,
  "end_date": null,
  "timezone": null
}
```

Output:

```json
{
  "provider": "",
  "retrieved_at": "",
  "forecast_type": "forecast",
  "location": "",
  "daily": [],
  "alerts": [],
  "source_refs": [],
  "error": null
}
```

The adapter must distinguish current forecast, historical climate, advisory, and stale cached data.

### Hotel Search Tool

Operation: `search_hotels`

Input:

```json
{
  "destination": "Goa, India",
  "check_in": null,
  "check_out": null,
  "adults": 1,
  "children": 0,
  "category": null,
  "maximum_total_price": null,
  "currency": "INR",
  "limit": 10
}
```

Output must include normalized hotel options, price basis, taxes and fees, availability observation time, cancellation information when available, provider, source references, and error status.

### Attraction Search Tool

Operation: `search_attractions`

Input:

```json
{
  "destination": "Goa, India",
  "start_date": null,
  "end_date": null,
  "interests": [],
  "budget_max": null,
  "weather_sensitivity": null,
  "limit": 20
}
```

Output must include normalized attraction options, location, category, duration, cost basis, opening constraints, weather sensitivity, accessibility metadata when available, retrieval time, provider, and source references.

## Caching Strategy

Use a layered, provider-aware cache:

- Weather: short TTL for forecasts and alerts; never use expired severe-weather alerts as current truth.
- Hotel search: short TTL keyed by destination, dates, party, currency, filters, provider, and request policy. Availability and price must retain observation time.
- Attractions: longer TTL for stable descriptions; shorter TTL for opening hours, closures, and prices.
- Policy and guardrail results: do not cache across materially different raw requests; cache only deterministic safe metadata where permitted.

Cache keys must include schema version, normalized parameters, locale, currency, and provider. Never cache user secrets. Return cache age and freshness metadata to agents. A stale value may be used only as a labeled fallback when policy permits.

## Retry and API Fallback Strategy

Classify failures as:

- `transient`: timeout, rate limit, temporary provider outage.
- `permanent`: invalid request, unsupported location, authentication failure.
- `degraded`: partial response, stale data, missing fields.

Retry only transient failures with bounded exponential backoff and jitter. Respect provider `Retry-After`. Do not retry policy or guardrail decisions blindly.

Weather fallback:

```text
Primary Weather API
        |
     failure
        v
Backup Weather API
        |
     failure
        v
Stale permitted cache or seasonal estimate, explicitly labeled
        |
  insufficient evidence
        v
Graceful user message and resumable failure
```

The same adapter pattern may be used for hotel and attraction providers. Fallback providers must be normalized to the same contract and must not silently lower required safety or data-quality thresholds.

A provider failure must never be converted into an empty successful result. Agents must receive `status: degraded` or `status: failed` with an actionable error code.

## Hallucination Reduction

- Constrain every agent to a JSON schema and reject extra or invalid fields where appropriate.
- Use tool evidence for current and factual claims.
- Attach evidence references to every price, weather statement, operating constraint, and availability claim.
- Separate observed facts, estimates, assumptions, and recommendations.
- Use deterministic budget arithmetic outside the LLM where possible.
- Use deterministic day-count and date validation.
- Prompt the Itinerary Agent to select only from supplied hotel and attraction candidates.
- Require the Reviewer Agent to identify unsupported claims.
- Preserve `null` for unknown values.
- Add freshness timestamps and confidence levels.
- Never claim a booking, reservation, API call, or source lookup that did not occur.
- Prevent agents from seeing untrusted raw tool text as instructions; treat it as data.

## Output Presentation Contract

The user-facing response may be natural language, but it must be rendered from the approved structured result. It should include:

- Destination, dates, duration, and party assumptions.
- Day-by-day itinerary.
- Hotel options and observed price basis.
- Budget breakdown with currency and estimates.
- Weather summary and relevant caveats.
- Preferences applied from memory, when material.
- Unresolved items and suggested next actions.
- Source freshness or "checked at" information where relevant.

Never expose internal prompts, hidden chain-of-thought, classifier thresholds, credentials, or raw provider payloads.

## Failure Handling

Use stable error codes and safe user messages. Examples:

- `INVALID_EXTRACTION`
- `MISSING_REQUIRED_INPUT`
- `POLICY_BLOCKED`
- `GUARDRAIL_BLOCKED`
- `WEATHER_WARNING_PENDING`
- `PROVIDER_TIMEOUT`
- `PROVIDER_RATE_LIMITED`
- `INSUFFICIENT_EVIDENCE`
- `BUDGET_INFEASIBLE`
- `REVIEW_FAILED`
- `WORKFLOW_LIMIT_REACHED`

User messages must be concise and actionable. Internal logs may contain diagnostic details, subject to redaction and access control.

When the budget is infeasible, do not silently exceed it. Offer structured choices such as fewer days, a lower hotel category, different dates, or another destination, and wait for user approval.

When no safe or sufficiently fresh weather data is available, explain that the plan cannot be validated reliably and allow the user to retry later or provide an alternative date range.

## Non-Functional Requirements

### Reliability

- Durable state and resumable workflows.
- Idempotent stage execution.
- Bounded retries and timeouts for every external dependency.
- Graceful degradation with explicit freshness and confidence.
- No silent data loss or success after partial failure.

### Performance and Cost

- Fan out independent validation and planning searches in parallel.
- Cache normalized provider data according to freshness requirements.
- Use small extraction and classification models where quality is sufficient.
- Use a larger model only for itinerary synthesis or review when needed.
- Pass compact structured summaries rather than full raw payloads between agents.
- Deduplicate identical tool calls within a request and session.
- Set token, tool-call, latency, and monetary budgets per request.
- Stop work immediately after terminal rejection.

### Security and Privacy

- Authenticate and authorize tool access.
- Keep provider credentials outside prompts and model-visible state.
- Redact secrets, payment data, and unnecessary personal data from logs.
- Encrypt persisted state and memory at rest and in transit.
- Apply retention and deletion policies to session memory and raw provider responses.
- Treat all user and provider text as untrusted input.

### Observability

Use structured logs for every workflow and stage. Each event must include:

- `timestamp`, `request_id`, `session_id`, `correlation_id`
- `workflow_version`, `schema_version`, `agent`, `stage`
- `status`, `latency_ms`, `retry_count`, `cache_hit`
- `provider`, `tool_call_id`, `error_code`
- `input_hash`, `output_hash`, and redaction metadata where appropriate

Do not log full sensitive prompts or secrets.

Collect metrics for:

- Requests by terminal state.
- Extraction validation and clarification rate.
- Policy and guardrail block rate.
- Weather warning and user continuation rate.
- Tool latency, error, timeout, rate-limit, and fallback rate.
- Cache hit ratio and stale-data usage.
- Average and p95 end-to-end latency.
- Token usage, model usage, tool-call count, and estimated cost.
- Reviewer approval, revision, and budget-infeasibility rate.
- Itinerary completeness and post-generation correction rate.

Trace fan-out and fan-in spans so the slowest dependency and failed branch are identifiable.

### Quality and Evaluation

Maintain a versioned evaluation set covering:

- Explicit destination and budget requests.
- Ambiguous destination, budget, and duration requests.
- Missing dates with fixed duration.
- Weather warnings, unavailable weather, and fallback providers.
- Prompt injections embedded in attraction or hotel names.
- Policy and guardrail failures.
- Memory exclusions and current-request overrides.
- Budget infeasibility and currency conversion cases.
- Provider partial results and stale cache behavior.
- Reviewer revision cycles and loop limits.

Measure schema validity, unsupported-claim rate, budget arithmetic accuracy, day completeness, policy false negatives, clarification quality, and tool-evidence coverage.

## Success Criteria

The implementation generated from this specification is successful when:

1. A request such as "Plan a 5-day Goa trip under INR 25,000" produces a complete, schema-valid itinerary or a precise clarification when required.
2. The extraction layer normalizes input without making recommendations.
3. Policy and guardrail failures terminate before planning and return generic safe responses.
4. Weather warnings pause for explicit user choice and re-run validation after a destination change.
5. Policy, guardrail, and weather validation execute in parallel and terminate deterministically.
6. Hotel and attraction searches execute in parallel after validation.
7. The itinerary contains the required number of days and a transparent budget calculation.
8. The reviewer rejects unsupported claims, missing days, schema violations, weather omissions, and budget violations.
9. Every agent communicates through versioned JSON contracts only.
10. Tool failures retry within bounds, use configured fallbacks, and never masquerade as successful data.
11. Session memory influences future recommendations while respecting current explicit instructions and user deletion controls.
12. Logs, metrics, traces, evidence references, and cost data are sufficient to diagnose a failed request without exposing secrets.
13. All workflow loops, retries, model calls, and external calls have explicit limits.
14. The system never claims that travel was booked or that uncertain information is guaranteed.
