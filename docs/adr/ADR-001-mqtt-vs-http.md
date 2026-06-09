# ADR-001 — Choosing MQTT over HTTP

## Context
A decision was needed regarding the communication protocol between the mock publisher, the broker, and the subscriber.

## Options Considered
- HTTP REST — simple but too verbose for IoT scenarios.
- WebSocket — supports bidirectional communication but adds complexity.
- MQTT — lightweight, publish/subscribe model, widely adopted in IoT.

## Decision
MQTT was chosen as the communication protocol.

## Reasons
- Industry-standard protocol for IoT devices.
- Lightweight and suitable for devices with limited resources.
- Publish/subscribe model enables easy integration of new components without modifying existing ones.

## Consequences
Requires deployment of a broker (e.g., containerized Mosquitto).

## Statut
✅ Implemented