#!/usr/bin/env python3

import random
import time
import json
import paho.mqtt.client as mqtt


class SmartPlug:
    def __init__(self, id, location, target_device, nominal_power, max_power):
        self.id = id
        self.location = location
        self.target_device = target_device
        self.nominal_power = nominal_power
        self.max_power = max_power

        self.connected = True
        self.is_used = False
        self.energy_consumption = 0
        self.plug_time = 0
        self.idle_time = 0
        self.is_broken = False

    def generate_data(self):
        if self.is_broken:
            return

        if random.random() < 0.02:
            self.connected = not self.connected

        if not self.connected:
            self.energy_consumption = 0
            self.is_used = False
            self.plug_time = 0
            self.idle_time = 0
        else:
            self.plug_time += 1 / 60

            if random.random() < 0.10:
                self.is_used = not self.is_used

            if self.is_used:
                if random.random() < 0.01:
                    self.energy_consumption = round(self.max_power * 1.2, 2)
                else:
                    self.energy_consumption = round(
                        self.nominal_power + random.uniform(-2, 2), 2
                    )
                self.idle_time = 0
            else:
                self.energy_consumption = round(random.uniform(0.5, 2.0), 2)
                self.idle_time += 1 / 60

        if self.energy_consumption > self.max_power:
            self.is_broken = True
            self.energy_consumption = 0
            self.is_used = False
            self.connected = False

    def to_json(self):
        return {
            "id": self.id,
            "location": self.location,
            "device": self.target_device,
            "connected": self.connected,
            "is_used": self.is_used,
            "energy": self.energy_consumption,
            "plug_time": round(self.plug_time, 2),
            "idle_time": round(self.idle_time, 2),
            "is_broken": self.is_broken
        }


# MQTT setup
client = mqtt.Client()
client.connect("localhost", 1883, 60)
client.loop_start()

# Load config
with open("devices_config.json", "r") as f:
    config = json.load(f)

plugs = [
    SmartPlug(
        d["id"],
        d["location"],
        d["target_device"],
        d["nominal_power"],
        d["max_power"],
    )
    for d in config["devices"]
]

print("MQTT SmartPlug publisher started...")

try:
    while True:
        for plug in plugs:
            plug.generate_data()

            payload = json.dumps(plug.to_json())

            topic = f"smartplug/{plug.id}"
            client.publish(topic, payload)

            print(f"Sent to {topic}: {payload}")

        time.sleep(1)

except KeyboardInterrupt:
    print("\nArrêt...")

client.loop_stop()
client.disconnect()