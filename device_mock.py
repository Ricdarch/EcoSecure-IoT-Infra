#!/usr/bin/env python3
import random
import time
import json
import os
import paho.mqtt.client as mqtt

class SmartPDU:
    def __init__(self, device_config):
        # Configuration mapping from JSON
        self.id = device_config["id"]
        self.location = device_config["location"]
        self.name = device_config["target_device"]
        self.workload = device_config["workload_type"]
        self.min_p = device_config["min_power"]
        self.nom_p = device_config["nominal_power"]
        self.safety = device_config["safety_threshold"]
        self.max_p = device_config["max_power"]
        self.nom_t = device_config["nominal_temp"]

        # Internal state initialization
        self.is_connected = True
        self.is_under_attack = False
        self.current_power = self.nom_p
        self.current_temp = self.nom_t
        self.total_energy_kwh = 0.0
        self.last_update = time.time()

    def simulate_behavior(self):
        """Simulates physical and network behavior of the PDU"""
        
        # --- Network Stability Simulation ---
        if not self.is_connected:
            # 1% chance to recover connection
            if random.random() < 0.01:
                self.is_connected = True
            self.current_power = 0
            return

        # 0.1% chance of random network drop
        if random.random() < 0.001:
            self.is_connected = False
            return

        # --- Power Consumption Simulation (kW) ---
        # 1% chance to trigger an anomaly/attack state
        if random.random() < 0.01:
            self.is_under_attack = not self.is_under_attack

        if self.is_under_attack:
            # Cyber-attack signature: High power draw near or above safety threshold
            # Simulates DDoS (CPU stress) or Crypto-jacking
            self.current_power = random.uniform(self.safety * 0.9, self.max_p * 1.1)
        else:
            # Normal behavior: Small fluctuations based on workload type
            variation = 0.5 if self.workload == "AI_TRAINING_GPU" else 0.1
            self.current_power = self.nom_p + random.uniform(-variation, variation)

        # --- Thermal Simulation ---
        # Temperature follows power draw with simulated thermal inertia
        temp_target = self.nom_t + (self.current_power * 2) 
        self.current_temp += (temp_target - self.current_temp) * 0.1

        # --- Energy Accumulation (kWh) ---
        now = time.time()
        interval = (now - self.last_update) / 3600  # Convert seconds to hours
        self.total_energy_kwh += self.current_power * interval
        self.last_update = now

    def get_payload(self):
        """Constructs the JSON payload for MQTT publishing"""
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


MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
CONFIG_FILE = os.getenv("CONFIG_FILE", "devices_config.json")

client = mqtt.Client()

def run():
    # Attempt to connect to the Broker
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
    except Exception as e:
        print(f"Failed to connect to broker: {e}")
        return

    # Load infrastructure configuration
    try:
        with open(CONFIG_FILE, "r") as f:
            config_data = json.load(f)
    except FileNotFoundError:
        print(f"Config file {CONFIG_FILE} not found!")
        return
    
    # Initialize PDU objects
    pdus = [SmartPDU(d) for d in config_data["devices"]]

    print(f"IoT Simulation started. Connected to Broker: {MQTT_BROKER}")

    try:
        while True:
            for pdu in pdus:
                pdu.simulate_behavior()
                
                # Dynamic topic structure: datacenter/rack_id/pdu_id/metrics
                topic = f"datacenter/{pdu.location.lower()}/{pdu.name.lower()}/metrics"
                payload = json.dumps(pdu.get_payload())
                
                client.publish(topic, payload)
                
            time.sleep(1) # 1Hz Refresh rate
    except KeyboardInterrupt:
        print("\nStopping simulator...")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    run()