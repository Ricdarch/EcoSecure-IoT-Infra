# ADR-001 — Choosing MQTT over HTTP

## Context
I had to choose a communication protocol between the mock publisher, the broker, and the subscriber.

## Options Considered
- HTTP REST — simple but too verbose for IoT
- WebSocket — bidirectional but complex to manage
- MQTT — lightweight, publish/subscribe, IoT standard

## Decision
I decided to choose the MQTT protocol.

## Reasons
- Industry-standard IoT protocol
- Lightweight — ideal for devices with limited resources
- The pub/sub model makes it easy to connect 
  new components without modifying existing ones

## Consequences
- Requires a broker (containerized Mosquitto)

## Statut
✅ Implemented