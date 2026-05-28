#!/usr/bin/env python3
import random
import time
import json
import os
import ssl
import logging
import dataclasses
import paho.mqtt.client as mqtt


@dataclasses
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
    current_power: float = nominal_power
    current_temp: float = nominal_temp
    total_energy_kwh: float = 0.0
    last_update: float = time.time()

    def simulate_behavior(self):
        """Simulates the physical and network behavior of the PDU"""
        if not self.is_connected:
            if random.random() < 0.01:  # 1% de chance of reconnection
                self.is_connected = True
            self.current_power = 0
            return

        if random.random() < 0.001:  # Random network outage
            self.is_connected = False
            return

        # Malfunction/attack simulation (1% chance)
        if random.random() < 0.01:
            self.is_under_attack = not self.is_under_attack

        if self.is_under_attack:
            # Attack signature: Power consumption near the critical threshold
            self.current_power = random.uniform(self.safety_threshold * 0.9, self.maximal_power * 1.1)
        else:
            # Normal fluctuations depending on the workload
            variation = 0.5 if self.workload == "AI_TRAINING_GPU" else 0.1
            self.current_power = self.nominal_power + random.uniform(-variation, variation)

        # Thermal Simulation (Inertia)
        temp_target = self.nominal_temp + (self.current_power * 2)
        self.current_temp += (temp_target - self.current_temp) * 0.1

        # Energy storage
        now = time.time()
        interval = (now - self.last_update) / 3600
        self.total_energy_kwh += self.current_power * interval
        self.last_update = now

    def get_payload(self):
        return {
            "id": self.id,
            "device": self.name,
            "location": self.location,
            "workload": self.workload,
            "metrics": {
                "power_kw": round(self.current_power, 3),
                "temp_c": round(self.current_temp, 1),
                "energy_kwh": round(self.total_energy_kwh, 4)
            },
            "status": {
                "connected": self.is_connected,
                "threat_detected": self.is_under_attack
            }
        }


# --- ENVIRONMENT CONFIGURATION ---
MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT"))
MQTT_TOKEN = os.getenv("MQTT_TOKEN")
CONFIG_FILE = os.getenv("CONFIG_FILE")
CERT_PATH = os.getenv("CERT_PATH")

# Client MQTT initialization
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)


def run():
    # 1. Authentification configuration
    client.username_pw_set("token_app", MQTT_TOKEN)

    # 2. Testament configuration (LWT)
    lwt_payload = json.dumps({"status": "OFFLINE", "msg": "Simulator crash"})
    client.will_set(
        "datacenter/status/simulator", lwt_payload, qos=1, retain=True)

    # 3. TLS onfiguration (Security)
    try:
        cert_path = CERT_PATH
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=cert_path)
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED

        client.tls_set_context(context)
        logging.info("✅ TLS configuration loaded successfully.")
    except Exception as e:
        logging.error(f"TLS config error: {e}")
        return

    # Connection
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
    except Exception as e:
        logging.error(f"Failed to connect to broker: {e}")
        return

    # Configuration loading
    try:
        with open(CONFIG_FILE, "r") as f:
            config_data = json.load(f)
    except Exception as e:
        logging.error(f"Error reading configuration: {e}")
        return

    pdus = [SmartPDU(d) for d in config_data["devices"]]
    logging.info(f"🚀 IoT Simulation started. Connected to: {MQTT_BROKER}")

    try:
        while True:
            for pdu in pdus:
                pdu.simulate_behavior()

                loc = pdu.location.lower()
                name = pdu.name.lower()
                topic = f"datacenter/{loc}/{name}/metrics"
                payload = json.dumps(pdu.get_payload())

                client.publish(topic, payload)

            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("\nStopping simulator...")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    run()
