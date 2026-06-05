#!/usr/bin/env python3
import asyncio
import json
import logging
import os
import random
import ssl
import time
from dataclasses import dataclass, field
import aiomqtt

# --- LOGGING ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- ENVIRONMENT CONFIGURATION ---
MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT", 8883))
USERNAME = os.getenv("USERNAME")
MQTT_TOKEN = os.getenv("MQTT_TOKEN")
CERT_PATH = os.getenv("CERT_PATH")
DEVICE_COUNT = int(os.getenv("DEVICE_COUNT", 100))
PUBLISH_INTERVAL = float(os.getenv("PUBLISH_INTERVAL", 1.0))

# Validate required env vars
for var in ["MQTT_BROKER", "MQTT_TOKEN", "CERT_PATH"]:
    if not os.getenv(var):
        raise EnvironmentError(
            f"Missing required environment variable: {var}"
        )

# --- SIMULATION CONFIGURATION ---
LOCATIONS = [
    "paris-dc1",
    "london-dc2",
    "berlin-dc3",
    "amsterdam-dc4",
    "madrid-dc5",
]

WORKLOAD_TYPES = [
    "AI_TRAINING_GPU",
    "WEB_SERVER",
    "DATABASE",
    "STORAGE",
    "NETWORK",
]


# ══════════════════════════════════════════════
#                   DEVICE CLASS
# ══════════════════════════════════════════════

@dataclass
class SmartPDU:
    id: int
    location: str
    name: str
    workload: str
    minimal_power: float
    nominal_power: float
    maximal_power: float
    safety_threshold: float
    nominal_temp: float

    # Internal state
    is_connected: bool = True
    is_under_attack: bool = False
    current_power: float = field(init=False)
    current_temp: float = field(init=False)
    total_energy_kwh: float = 0.0
    last_update: float = field(default_factory=time.time)

    def __post_init__(self):
        self.current_power = self.nominal_power
        self.current_temp = self.nominal_temp

    async def simulate_behavior(self):
        """Simulates the physical and network behavior of the PDU."""
        if not self.is_connected:
            if random.random() < 0.01:
                self.is_connected = True
                logger.info(f"[{self.name}] Reconnected")
            self.current_power = 0
            return

        if random.random() < 0.001:
            self.is_connected = False
            logger.warning(f"[{self.name}] Network outage")
            return

        # Cyber attack simulation (1% chance)
        if random.random() < 0.01:
            self.is_under_attack = not self.is_under_attack

        if self.is_under_attack:
            self.current_power = random.uniform(
                self.safety_threshold * 0.9,
                self.maximal_power * 1.1
            )
        else:
            variation = 0.5 if self.workload == "AI_TRAINING_GPU" else 0.1
            self.current_power = self.nominal_power + random.uniform(
                -variation, variation
            )

        # Thermal simulation with inertia
        temp_target = self.nominal_temp + (self.current_power * 2)
        self.current_temp += (temp_target - self.current_temp) * 0.1

        # Energy accumulation
        now = time.time()
        interval = (now - self.last_update) / 3600
        self.total_energy_kwh += self.current_power * interval
        self.last_update = now

    def get_payload(self) -> dict:
        return {
            "id": self.id,
            "device": self.name,
            "location": self.location,
            "workload": self.workload,
            "metrics": {
                "power_kw":   round(self.current_power, 3),
                "temp_c":     round(self.current_temp, 1),
                "energy_kwh": round(self.total_energy_kwh, 4),
            },
            "status": {
                "connected":       self.is_connected,
                "threat_detected": self.is_under_attack,
            }
        }


# ══════════════════════════════════════════════
#                  DEVICE GENERATION
# ══════════════════════════════════════════════

def generate_pdus(count: int) -> list:
    """Dynamically generate a fleet of SmartPDU devices."""
    pdus = []
    for i in range(count):
        nominal = random.uniform(1.0, 10.0)
        pdus.append(SmartPDU(
            id=i,
            name=f"pdu-{i:04d}",
            location=random.choice(LOCATIONS),
            workload=random.choice(WORKLOAD_TYPES),
            minimal_power=round(nominal * 0.5, 2),
            nominal_power=round(nominal, 2),
            maximal_power=round(nominal * 1.5, 2),
            safety_threshold=round(nominal * 1.3, 2),
            nominal_temp=round(random.uniform(20.0, 35.0), 1),
        ))
    logger.info(f"Generated {count} SmartPDU devices")
    return pdus


# ══════════════════════════════════════════════
#                 ASYNC SIMULATION
# ══════════════════════════════════════════════

async def simulate_device(pdu: SmartPDU, client: aiomqtt.Client) -> None:
    """Independent coroutine for each SmartPDU."""
    while True:
        await pdu.simulate_behavior()

        if pdu.is_connected:
            topic = f"datacenter/{pdu.location}/{pdu.name}/metrics"
            payload = json.dumps(pdu.get_payload())

            try:
                await client.publish(topic, payload, qos=1)
                logger.debug(f"Published → {topic}")
            except Exception as e:
                logger.error(f"Publish error [{pdu.name}]: {e}")

        await asyncio.sleep(PUBLISH_INTERVAL)


# ══════════════════════════════════════════════
#                    MAIN
# ══════════════════════════════════════════════

async def main() -> None:
    """Main entry point."""

    # Generate devices
    pdus = generate_pdus(DEVICE_COUNT)

    # TLS configuration
    tls_context = ssl.create_default_context(
        ssl.Purpose.SERVER_AUTH,
        cafile=CERT_PATH
    )
    tls_context.check_hostname = True
    tls_context.verify_mode = ssl.CERT_REQUIRED

    # LWT — Last Will and Testament
    will = aiomqtt.Will(
        topic="datacenter/status/simulator",
        payload=json.dumps({
            "status": "OFFLINE",
            "msg": "Simulator crash"
        }),
        qos=1,
        retain=True,
    )

    logger.info(
        f"🚀 Connecting to {MQTT_BROKER}:{MQTT_PORT} "
        f"with {DEVICE_COUNT} devices..."
    )

    try:
        async with aiomqtt.Client(
            hostname=MQTT_BROKER,
            port=MQTT_PORT,
            username=USERNAME,
            password=MQTT_TOKEN,
            tls_context=tls_context,
            will=will,
        ) as client:
            logger.info("✅ Connected. Starting simulation...")

            # Launch one coroutine per device
            await asyncio.gather(*[
                simulate_device(pdu, client)
                for pdu in pdus
            ])

    except aiomqtt.MqttError as e:
        logger.error(f"MQTT connection error: {e}")
    except KeyboardInterrupt:
        logger.info("Simulation stopped by user.")


if __name__ == "__main__":
    asyncio.run(main())
