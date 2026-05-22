import paho.mqtt.client as mqtt
import json
import os
import ssl
import logging

# Logger configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- ENVIRONMENT CONFIGURATION ---
MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT"))
MQTT_TOKEN = os.getenv("MQTT_TOKEN")
CERT_PATH = os.getenv("CERT_PATH")

# Decision threshold (Edge computing)
TEMP_CRITIQUE = 45.0  # On alerte si > 45°C
POWER_THRESHOLD = 0.8  # On alerte si la conso varie brusquement


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        logging.info("✅ Edge Gateway operational. Listening to local stream...")
        # Subscribe to all topics
        client.subscribe("datacenter/#")
    else:
        logging.error(f"❌ Connection error : {reason_code}")


def on_message(client, userdata, msg):
    try:
        # 1. Reception and decoding
        payload = json.loads(msg.payload.decode())
        device_id = payload.get("id")
        metrics = payload.get("metrics", {})
        status = payload.get("status", {})

        # 2. Filtrering logic (Decision Making)
        is_urgent = False
        reasons = []

        # Test A: Threat detected by the PDU itself
        if status.get("threat_detected"):
            is_urgent = True
            reasons.append("CYBER_THREAT")

        # Test B : Temperature exceeds the threshold configured on the Edge
        if metrics.get("temp_c", 0) > TEMP_CRITIQUE:
            is_urgent = True
            reasons.append(f"OVERHEAT({metrics['temp_c']}°C)")

        # 3. Edge computing action
        if is_urgent:
            logging.warning(
                f"[CLOUD ALERT PDU: {device_id} | "
                f"Raisons: {reasons}")
            # Later, you'll put this here: cloud_client.publish(...)
        else:
            # Edge computing retains the normal data
            logging.info(f"[LOG LOCAL] {device_id}: Temp={metrics['temp_c']}°C - OK")

    except Exception as e:
        logging.error(f"⚠️ Erreur analyse message : {e}")


# --- INITIALIZATION ---
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

# Authentification and TLS
client.username_pw_set("token_app", MQTT_TOKEN)
context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=CERT_PATH)
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE
client.tls_set_context(context)

try:
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()
except KeyboardInterrupt:
    logging.info("Stopping Edge Gateway.")
finally:
    client.loop_stop()
    client.disconnect()
