import time
import json
import paho.mqtt.client as mqtt


class SmartPDU:
    def __init__(self, config):
        self.id = config["id"]
        self.role = config.get("role", "primary")
        self.location = config["location"]
        self.pdu_temp = 25.0
        self.fan_speed = 20.0
        self.current_power = 0.0
        self.workload_limit = 1.0
        self.status = "ONLINE"
        self.is_running = True

    def update_physics(self, room_temp):
        if not self.is_running:
            self.pdu_temp -= (self.pdu_temp - room_temp) * 0.05
            return

        if self.pdu_temp > 45:
            self.fan_speed = min(100, 20 + (self.pdu_temp - 45) * 2.6)
        else:
            self.fan_speed = 20

        heat_gen = (self.current_power / 1000) * 0.6
        cooling = (self.fan_speed / 100) * (self.pdu_temp - room_temp) * 0.15
        self.pdu_temp += (heat_gen - cooling)

        if self.pdu_temp >= 80:
            self.status = "EMERGENCY_SHUTDOWN"
            self.is_running = False
        elif self.pdu_temp >= 70:
            self.status = "CRITICAL_THROTTLING"
            self.workload_limit = 0.5
        else:
            self.status = "ONLINE"
            self.workload_limit = 1.0

    def set_load(self, base_power):
        if self.is_running:
            self.current_power = base_power * self.workload_limit


class Datacenter:
    def __init__(self):
        self.room_temp = 22.0
        self.target_temp = 22.0
        self.pdus = []

    def add_pdu(self, pdu):
        self.pdus.append(pdu)

    def manage_failover(self):
        for pdu in self.pdus:
            if pdu.role == "primary":
                backup = next((p for p in self.pdus if p.role == "backup"
                               and p.location == pdu.location), None)
                if not pdu.is_running and backup:
                    backup.set_load(2500)
                elif pdu.is_running:
                    pdu.set_load(2500)
                    if backup:
                        backup.set_load(50)

    def update_environment(self):
        total_heat = sum(p.current_power for p in self.pdus) / 10000
        self.room_temp += total_heat
        self.room_temp -= (self.room_temp - self.target_temp) * 0.1


def main():
    dc = Datacenter()
    configs = [
        {"id": "PDU-01-A", "location": "Rack-1", "role": "primary"},
        {"id": "PDU-01-B", "location": "Rack-1", "role": "backup"}
    ]
    for cfg in configs:
        dc.add_pdu(SmartPDU(cfg))

    client = mqtt.Client()
    # client.connect("localhost", 1883)

    try:
        while True:
            dc.manage_failover()
            dc.update_environment()
            for pdu in dc.pdus:
                pdu.update_physics(dc.room_temp)
                topic = f"dc/{pdu.location}/{pdu.id}".lower()
                payload = json.dumps({"temp": round(pdu.pdu_temp, 1)})
                # On utilise les variables pour éviter l'erreur F841
                print(f"Topic: {topic} | Payload: {payload}")
                # client.publish(topic, payload)
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopped.")


if __name__ == "__main__":
    main()