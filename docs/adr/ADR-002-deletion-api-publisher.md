# ADR-002 — Removal of the API between the publisher and the broker

## Context
In the initial design, I envisioned a REST API between the mock publisher and the MQTT broker to manage communication between the two.

## Initial Idea
Publisher → REST API → MQTT Broker

## Why I abandoned this idea
As I analyzed the role of each component, I realized that MQTT is itself a communication protocol; adding an API between the two would have amounted to unnecessarily duplicating that responsibility.

The API would have introduced:
- Additional latency
- Another point of failure
- Complexity with no added value

## Final Decision
Publisher → Direct MQTT → Broker

## What I Learned
A good distributed system minimizes unnecessary intermediaries. Each component must have a clear and single responsibility (Single Responsibility Principle).

## Status
✅ Decision approved and implemented