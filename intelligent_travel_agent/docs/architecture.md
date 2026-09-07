# Architecture

The system uses a Travel Request Understanding Layer, then input guardrails, an async validation fan-out/fan-in, parallel planning searches, itinerary synthesis, and independent review. Pydantic models are the only agent communication boundary. Provider clients are isolated behind retry, fallback, and TTL cache adapters.
