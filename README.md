# EcoSecure-IoT-Infra (R&D)

Core Vision: Build a secure Edge-to-Cloud gateway that acts as an intelligent filter for IoT telemetry.

📊 Data Classification Logic (The "Green" Engine)
The Edge layer classifies incoming MQTT messages into 5 categories to optimize cloud storage and energy:

Valid: Standard data -> Forward to Cloud.

Incomplete but Useful: Degraded data (due to connectivity issues) -> Process & Forward.

Anomaly (Observational): Strange patterns -> Flag for monitoring.

Useless: Redundant/Noise -> Ignore (Zero Cloud cost).

Dangerous: Malformed/Threats -> Reject & Alert (Security).

🛡️ Security Roadmap
Authentication: Mutual TLS (mTLS) for device-to-broker trust.

Resilience: "Last Will and Testament" (LWT) to handle unexpected device disconnections.

🛠️ Current Status
[ ] Build Basic Device Mock (Random sensor data).

[ ] Setup MQTT Broker (Mosquitto/EMQX).

[ ] Implement Edge Filtering Logic (The 5-tier classifier).

[ ] Hardening: mTLS & LWT.
