# ADR-004 — Event Streaming Technology: RabbitMQ vs Apache Kafka vs Redpanda

## Context

The EcoSecure platform processes telemetry from thousands of concurrent IoT devices
(SmartPDUs) via MQTT. The edge gateway filters critical events and must forward them
to the cloud for storage, alerting and dashboarding.

As the number of simulated devices grows (asyncio publisher — 100 to 10,000+ devices),
the edge gateway began showing backpressure symptoms:

```
iot_publisher | WARNING - There are 16 pending publish calls.
iot_publisher | WARNING - There are 18 pending publish calls.
```

This confirmed the need for a **message buffer** between the edge layer and the cloud —
a system that could absorb traffic spikes, guarantee message delivery, and decouple
producers from consumers.

Three candidates were evaluated: **RabbitMQ**, **Apache Kafka**, and **Redpanda**.

---

## Options Considered

### Option 1 — RabbitMQ

RabbitMQ is a traditional message broker implementing the AMQP protocol. It uses
a push-based model where the broker delivers messages to consumers.

**Strengths**
- Simple to set up and operate
- Supports multiple protocols: AMQP, MQTT, STOMP
- Good UI dashboard out of the box
- Well-suited for task queues and RPC patterns
- Lighter resource footprint than Kafka

**Weaknesses**
- Messages are deleted after acknowledgement — no replay capability
- Not designed for high-throughput time-series data
- Horizontal scaling is complex compared to Kafka
- No native concept of ordered, partitioned log
- Less relevant for IoT telemetry pipelines at scale

**Verdict:** Good for task queuing and microservices — not the right fit for
an IoT event streaming platform where replay, ordering and retention matter.

---

### Option 2 — Apache Kafka ✅ Selected

Apache Kafka is a distributed event streaming platform built around a
persistent, partitioned, ordered log. Producers write to topics, consumers
read at their own pace using offsets.

**Strengths**
- Industry standard for IoT and real-time data pipelines
- Messages are retained on disk — full replay capability ✅
- Horizontal scaling via partitions — handles millions of events/second
- Multiple independent consumers on the same topic (fan-out) ✅
- Backpressure management by design — consumers control their read pace ✅
- Rich ecosystem: Kafka Streams, Kafka Connect, Schema Registry
- Strimzi operator available for Kubernetes deployment ✅
- `aiokafka` library for Python asyncio — consistent with existing stack ✅
- Used in production at LinkedIn, Uber, Netflix, Airbus, Orange

**Weaknesses**
- Heavier resource footprint (JVM-based)
- Historically required ZooKeeper (now replaced by KRaft in Kafka 3.x+)
- Steeper learning curve than RabbitMQ
- Operational complexity at scale

**Why Kafka fits EcoSecure specifically:**

The edge gateway generates two types of events:
- `iot.alerts` — critical events (CYBER_THREAT, OVERHEAT, POWER_SPIKE)
- `iot.telemetry` — normal device metrics

Kafka's topic/partition model maps perfectly to this separation. Multiple
consumers can independently read from `iot.alerts` — one to forward to
AWS IoT Core, another to trigger CloudWatch alarms, another to feed Grafana —
without any coupling between them.

The replay capability is also directly useful: if the AWS IoT Core consumer
goes down temporarily, it resumes from its last offset when it comes back.
No data is lost.

---

### Option 3 — Redpanda

Redpanda is a Kafka-compatible streaming platform rewritten in C++ (no JVM,
no ZooKeeper). It implements the full Kafka API — any Kafka client works
with Redpanda without code changes.

**Strengths**
- Kafka API compatible — zero code changes required ✅
- Written in C++ — significantly lower latency and resource usage
- No ZooKeeper, no JVM — simpler operations
- Single binary deployment
- 10x lower tail latency than Kafka in benchmarks
- Growing enterprise adoption

**Weaknesses**
- Younger project — smaller ecosystem and community than Kafka
- Strimzi operator does not support Redpanda natively
- Fewer production case studies and battle-tested deployments
- Less documentation and community resources for troubleshooting
- For this project's scale, performance gains over Kafka are not needed

**Verdict:** Technically superior to Kafka on performance metrics — but the
ecosystem maturity gap and lack of Strimzi support on Kubernetes makes it
a risk for a learning-focused project. Redpanda is a strong candidate for
a future production deployment.

---

## Decision

**Apache Kafka — deployed via Strimzi operator on K3s.**

---

## Rationale

| Criteria | RabbitMQ | Kafka | Redpanda |
|---|---|---|---|
| IoT telemetry at scale | ⚠️ Limited | ✅ Native | ✅ Native |
| Message replay | ❌ No | ✅ Yes | ✅ Yes |
| Backpressure management | ⚠️ Partial | ✅ By design | ✅ By design |
| Multi-consumer fan-out | ⚠️ Complex | ✅ Native | ✅ Native |
| Kubernetes (Strimzi) | ❌ No | ✅ Yes | ⚠️ Partial |
| Python asyncio support | ✅ aio-pika | ✅ aiokafka | ✅ aiokafka |
| Resource footprint | 🟢 Light | 🔴 Heavy | 🟡 Medium |
| Ecosystem maturity | 🟢 Mature | 🟢 Mature | 🟡 Growing |
| Learning value for CV | 🟡 Medium | 🟢 High | 🟡 Medium |

The decision is driven by four factors:

**1 — Backpressure management is the primary need.**
The publisher generates bursts of messages that overwhelm the edge gateway.
Kafka's consumer-offset model solves this by design — the edge gateway reads
from Kafka at its own pace, regardless of the publisher's throughput.

**2 — Replay capability matters for IoT.**
If the AWS IoT Core consumer fails, Kafka retains the events. RabbitMQ would
lose them. For a datacenter monitoring platform, this is not acceptable.

**3 — Industry alignment.**
Kafka is the de-facto standard for IoT event streaming pipelines at companies
like Orange, Airbus, Schneider Electric — the exact employers targeted by
this project. Demonstrating Kafka proficiency directly addresses the skill
gap for IoT Platform Engineer roles.

**4 — Strimzi on Kubernetes.**
The Strimzi operator provides a production-grade Kafka deployment on K3s with
a single Kubernetes manifest. This aligns with the project's Kubernetes-first
deployment strategy and provides a natural bridge to the AWS cloud layer.

---

## Architecture Impact

```
Before ADR-009
Publisher → MQTT → Mosquitto → Edge Gateway → [TODO: cloud]

After ADR-009
Publisher → MQTT → Mosquitto → Edge Gateway → Kafka (Strimzi/K3s)
                                                      │
                               ┌──────────────────────┤
                               │                      │
                        iot.alerts             iot.telemetry
                               │
                        Kafka Consumer
                               │
                        AWS IoT Core → Timestream → Grafana
```

---

## Consequences

- Edge Gateway (`subscriber.py`) becomes a **Kafka producer** using `aiokafka`
- Two Kafka topics created: `iot.alerts` and `iot.telemetry`
- Strimzi operator deployed on K3s namespace `kafka`
- A new Kafka consumer service will be implemented (Python or Go) to forward
  events to AWS IoT Core
- The `# TODO: forward to Kafka` comment in `subscriber.py` will be replaced
  with a real `aiokafka` producer call

---

## Future Consideration — Redpanda

If EcoSecure evolves into a production system with strict latency requirements
(<1ms tail latency), Redpanda should be reconsidered. Its Kafka API compatibility
means zero migration cost — only the deployment changes.

---

## References

- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Strimzi — Kafka on Kubernetes](https://strimzi.io)
- [Redpanda Documentation](https://docs.redpanda.com)
- [aiokafka — Python asyncio Kafka client](https://aiokafka.readthedocs.io)
- [Kafka vs RabbitMQ — Confluent](https://www.confluent.io/blog/kafka-vs-rabbitmq/)