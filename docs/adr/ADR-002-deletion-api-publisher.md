# ADR-002 — Removal of the API between the publisher and the broker

## Context
The initial design included a REST API between the mock publisher and the MQTT broker to manage their communication.

## Initial Design
Publisher → REST API → MQTT Broker

## Rationale for Abandoning the API
Upon review, it became clear that MQTT already serves as a communication protocol. Introducing an additional API would have duplicated responsibilities without providing real benefits.

The API would have introduced:

- Additional latency
- Another potential point of failure
- Unnecessary complexity

## Final Decision
Publisher → Direct MQTT → Broker

## Lessons Learned
A well-designed distributed system minimizes unnecessary intermediaries. Each component should have a clear, single responsibility, in line with the Single Responsibility Principle.

## Status
✅ Approved and implemented