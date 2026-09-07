# Contracts

Contracts live in `travel_planner/schemas`. Every agent accepts and returns Pydantic models. `TravelRequest.is_complete()` is the downstream execution gate; validation and planning workflows reject incomplete requests.
