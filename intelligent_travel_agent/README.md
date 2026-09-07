# Intelligent Travel Planner

A typed, async reference implementation of the architecture in `skill.md`.

## Run

```powershell
python -m pip install -e .
python -m travel_planner.main
pytest
```

The provider clients expose retry, fallback, TTL cache, and adapter boundaries for real APIs. Until those external providers are configured, planning stops with `REQUIRES_PROVIDER` rather than fabricating travel data. The orchestration path is:

1. Extraction, schema validation, and clarification.
2. Input guardrails.
3. Parallel policy, guardrail, and weather validation.
4. Human weather decision when needed.
5. Parallel hotel and attraction search.
6. Itinerary synthesis and independent review.
