import paho.mqtt.client as mqtt
import json
import os
import ssl

# --- CONFIGURATION (Identique à ton Publisher) ---
MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT"))
MQTT_TOKEN = os.getenv("MQTT_TOKEN")
CERT_PATH = os.getenv("CERT_PATH")

# Seuils de décision (Logique Edge)
TEMP_CRITIQUE = 45.0  # On alerte si > 45°C
POWER_THRESHOLD = 0.8  # On alerte si la conso varie brusquement


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("✅ Edge Gateway opérationnelle. Écoute du flux local...")
        # On s'abonne à tous les capteurs du datacenter
        client.subscribe("datacenter/#")
    else:
        print(f"❌ Erreur de connexion : {reason_code}")


def on_message(client, userdata, msg):
    try:
        # 1. Réception et décodage
        payload = json.loads(msg.payload.decode())
        device_id = payload.get("id")
        metrics = payload.get("metrics", {})
        status = payload.get("status", {})

        # 2. Logique de filtrage (Decision Making)
        is_urgent = False
        reasons = []

        # Test A : Menace détectée par le PDU lui-même
        if status.get("threat_detected"):
            is_urgent = True
            reasons.append("CYBER_THREAT")

        # Test B : Température dépasse le seuil configuré sur l'Edge
        if metrics.get("temp_c", 0) > TEMP_CRITIQUE:
            is_urgent = True
            reasons.append(f"OVERHEAT({metrics['temp_c']}°C)")

        # 3. Action de l'Edge
        if is_urgent:
            print(f"[ALERTE CLOUD POTENTIELLE] PDU: {device_id} | Raisons: {reasons}")
            # Plus tard, ici tu mettras : cloud_client.publish(...)
        else:
            # L'edge garde les données normales
            print(f"[LOG LOCAL] {device_id}: Temp={metrics['temp_c']}°C - OK")

    except Exception as e:
        print(f"⚠️ Erreur analyse message : {e}")


# --- INITIALISATION ---
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

# Authentification et TLS
client.username_pw_set("token_app", MQTT_TOKEN)
context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=CERT_PATH)
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE
client.tls_set_context(context)

try:
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()
except KeyboardInterrupt:
    print("Arrêt de l'Edge Gateway.")
