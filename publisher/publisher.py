#!/usr/bin/env python3
import random
import time
import json
import os
import ssl
import paho.mqtt.client as mqtt


class SmartPDU:
    def __init__(self, device_config):
        # Mapping de la configuration JSON
        self.id = device_config["id"]
        self.location = device_config["location"]
        self.name = device_config["target_device"]
        self.workload = device_config["workload_type"]
        self.min_p = device_config["min_power"]
        self.nom_p = device_config["nominal_power"]
        self.safety = device_config["safety_threshold"]
        self.max_p = device_config["max_power"]
        self.nom_t = device_config["nominal_temp"]

        # État interne
        self.is_connected = True
        self.is_under_attack = False
        self.current_power = self.nom_p
        self.current_temp = self.nom_t
        self.total_energy_kwh = 0.0
        self.last_update = time.time()

    def simulate_behavior(self):
        """Simule le comportement physique et réseau du PDU"""
        if not self.is_connected:
            if random.random() < 0.01:  # 1% de chance de reconnexion
                self.is_connected = True
            self.current_power = 0
            return

        if random.random() < 0.001:  # Chute réseau aléatoire
            self.is_connected = False
            return

        # Simulation d'anomalie/attaque (1% de chance)
        if random.random() < 0.01:
            self.is_under_attack = not self.is_under_attack

        if self.is_under_attack:
            # Signature d'attaque : Consommation proche du seuil critique
            self.current_power = random.uniform(
                self.safety * 0.9, self.max_p * 1.1
            )
        else:
            # Fluctuations normales selon le workload
            variation = 0.5 if self.workload == "AI_TRAINING_GPU" else 0.1
            self.current_power = self.nom_p + random.uniform(
                -variation, variation
            )

        # Simulation thermique (Inertie)
        temp_target = self.nom_t + (self.current_power * 2)
        self.current_temp += (temp_target - self.current_temp) * 0.1

        # Accumulation énergie
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


# --- CONFIGURATION ENVIRONNEMENT ---
MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT"))
MQTT_TOKEN = os.getenv("MQTT_TOKEN")
CONFIG_FILE = os.getenv("CONFIG_FILE")
CERT_PATH = os.getenv("CERT_PATH")

# Initialisation Client MQTT
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)


def run():
    # 1. Configuration de l'Authentification
    client.username_pw_set("token_app", MQTT_TOKEN)

    # 2. Configuration du Testament (LWT)
    lwt_payload = json.dumps({"status": "OFFLINE", "msg": "Simulator crash"})
    client.will_set(
        "datacenter/status/simulator", lwt_payload, qos=1, retain=True
    )

    # 3. Configuration TLS (Sécurité)
    try:
        cert_path = CERT_PATH
        context = ssl.create_default_context(
            ssl.Purpose.SERVER_AUTH, cafile=cert_path
        )
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        client.tls_set_context(context)
        print("✅ Configuration TLS chargée avec succès.")
    except Exception as e:
        print(f"Erreur config TLS: {e}")
        return

    # Connexion
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
    except Exception as e:
        print(f"Failed to connect to broker: {e}")
        return

    # Chargement Config
    try:
        with open(CONFIG_FILE, "r") as f:
            config_data = json.load(f)
    except Exception as e:
        print(f"Erreur lecture config: {e}")
        return

    pdus = [SmartPDU(d) for d in config_data["devices"]]
    print(f"🚀 IoT Simulation started. Connected to: {MQTT_BROKER}")

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
        print("\nStopping simulator...")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    run()
