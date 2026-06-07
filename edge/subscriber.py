#!/usr/bin/env python3
import asyncio
import json
import logging
import os
import ssl

import aiomqtt

# --- LOGGING ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- ENVIRONMENT CONFIGURATION ---
MQTT_BROKER    = os.getenv("MQTT_BROKER",)
MQTT_PORT      = int(os.getenv("MQTT_PORT"))
USERNAME       = os.getenv("USERNAME")
MQTT_TOKEN     = os.getenv("MQTT_TOKEN")
CERT_PATH      = os.getenv("CERT_PATH")

# Validate required env vars
for var in ["MQTT_BROKER", "MQTT_TOKEN", "CERT_PATH"]:
    if not os.getenv(var):
        raise EnvironmentError(
            f"Missing required environment variable: {var}"
        )

# --- EDGE FILTERING THRESHOLDS ---
TEMP_CRITICAL   = float(os.getenv("TEMP_CRITICAL", 45.0))
POWER_THRESHOLD = float(os.getenv("POWER_THRESHOLD", 0.8))
CPU_THRESHOLD   = float(os.getenv("CPU_THRESHOLD", 85.0))


# ══════════════════════════════════════════════
# FILTERING LOGIC
# ══════════════════════════════════════════════

def should_forward_to_cloud(payload: dict) -> tuple[bool, list[str]]:
    """
    Core edge filtering logic.
    Returns (is_urgent, reasons).
    Only urgent events are forwarded to the cloud.
    """
    metrics = payload.get("metrics", {})
    status  = payload.get("status", {})
    reasons = []

    # Rule 1 — Cyber threat detected by the device
    if status.get("threat_detected"):
        reasons.append("CYBER_THREAT")

    # Rule 2 — Temperature exceeds critical threshold
    temp = metrics.get("temp_c")
    if temp is not None and temp > TEMP_CRITICAL:
        reasons.append(f"OVERHEAT({temp}°C > {TEMP_CRITICAL}°C)")

    # Rule 3 — Power consumption exceeds safety threshold
    power   = metrics.get("power_kw", 0)
    nominal = payload.get("nominal_power", 0)
    if nominal > 0 and power > nominal * (1 + POWER_THRESHOLD):
        reasons.append(f"POWER_SPIKE({power}kW)")

    # Rule 4 — Camera CPU overload
    cpu = metrics.get("cpu_usage")
    if cpu is not None and cpu > CPU_THRESHOLD:
        reasons.append(f"CPU_OVERLOAD({cpu}%)")

    return len(reasons) > 0, reasons


# ══════════════════════════════════════════════
# MESSAGE PROCESSING
# ══════════════════════════════════════════════

async def process_message(message: aiomqtt.Message) -> None:
    """
    Process a single MQTT message.
    Apply filtering logic and forward to cloud if urgent.
    """
    try:
        # 1. Decode incoming MQTT message
        payload   = json.loads(message.payload.decode())
        device_id = payload.get("id", "unknown")
        topic     = message.topic

        # 2. Apply edge filtering logic
        is_urgent, reasons = should_forward_to_cloud(payload)

        # 3. Edge action
        if is_urgent:
            logger.warning(
                f"[CLOUD ALERT] Device: {device_id} | "
                f"Topic: {topic} | "
                f"Reasons: {reasons}"
            )
            # TODO — Phase 2: forward to Kafka
            # await kafka_producer.send("iot.alerts", payload)

        else:
            logger.info(
                f"[LOCAL LOG] Device: {device_id} | "
                f"Topic: {topic} | OK"
            )

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON on {message.topic}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error processing message: {e}")


# ══════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════

async def main() -> None:
    """Main entry point."""

    # TLS configuration
    tls_context = ssl.create_default_context(
        ssl.Purpose.SERVER_AUTH,
        cafile=CERT_PATH
    )
    tls_context.check_hostname = True
    tls_context.verify_mode    = ssl.CERT_REQUIRED

    # LWT — Last Will and Testament
    will = aiomqtt.Will(
        topic="datacenter/status/edge-gateway",
        payload=json.dumps({
            "status": "OFFLINE",
            "msg":    "Edge Gateway disconnected unexpectedly"
        }),
        qos=1,
        retain=True,
    )

    logger.info(f"🚀 Connecting to {MQTT_BROKER}:{MQTT_PORT}...")

    # Reconnection loop — si le broker tombe, on reconnecte
    reconnect_interval = 5

    while True:
        try:
            async with aiomqtt.Client(
                hostname=MQTT_BROKER,
                port=MQTT_PORT,
                username=USERNAME,
                password=MQTT_TOKEN,
                tls_context=tls_context,
                will=will,
            ) as client:

                logger.info(
                    f"✅ Edge Gateway connected to {MQTT_BROKER}:{MQTT_PORT}"
                )

                # Subscribe to all datacenter topics
                await client.subscribe("datacenter/#", qos=1)
                logger.info("Subscribed to datacenter/#")

                # Process messages as they arrive
                async for message in client.messages:
                    await process_message(message)

        except aiomqtt.MqttError as e:
            logger.warning(
                f"Connection lost: {e}. "
                f"Reconnecting in {reconnect_interval}s..."
            )
            await asyncio.sleep(reconnect_interval)

        except KeyboardInterrupt:
            logger.info("Edge Gateway stopped by user.")
            break


if __name__ == "__main__":
    asyncio.run(main())