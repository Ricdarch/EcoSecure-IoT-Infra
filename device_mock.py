#!/usr/bin/env python3

import random
import time
import json

class SmartPlug:
    def __init__(self, id, location, target_device, nominal_power, max_power):
        # Statics data
        self.id = id
        self.location = location
        self.target_device = target_device
        self.nominal_power = nominal_power
        self.max_power = max_power
        
        # Dynamic state
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
            self.plug_time += 1/60 
            
            if random.random() < 0.10:
                self.is_used = not self.is_used

            if self.is_used:
                if random.random() < 0.01:
                    self.energy_consumption = round(self.max_power * 1.2, 2)
                else:
                    self.energy_consumption = round(self.nominal_power + random.uniform(-2, 2), 2)
                
                self.idle_time = 0
            else:
                self.energy_consumption = round(random.uniform(0.5, 2.0), 2)
                self.idle_time += 1/60

        if self.energy_consumption > self.max_power:
            self.is_broken = True
            self.energy_consumption = 0
            self.is_used = False
            self.connected = False

    def __str__(self):
        if self.is_broken:
            return f"[{self.location}] ID:{self.id} | !!! DISJONCTEUR SAUTÉ (Surcharge) !!!"
        
        state = "ON " if self.is_used else "OFF"
        conn = "CONN" if self.connected else "DISC"
        return (f"[{self.location:^10}] {self.target_device:^12} | {conn} | "
                f"Mode:{state} | {self.energy_consumption:>7}W | Time:{self.plug_time:>5.2f}h")

try:
    with open('devices_config.json', 'r') as f:
        config = json.load(f)
        plugs = [
            SmartPlug(
                d['id'], 
                d['location'], 
                d['target_device'], 
                d['nominal_power'], 
                d['max_power']
            ) for d in config["devices"]
        ]

    print("="*80)
    print(f"{'SMART PLUG MONITORING SYSTEM':^80}")
    print("="*80)

    while True:
        for plug in plugs:
            plug.generate_data()
            print(plug)
        
        print("-" * 80)
        time.sleep(1)

except FileNotFoundError:
    print("Erreur : Le fichier 'devices_config.json' est introuvable.")
except KeyboardInterrupt:
    print("\nArrêt du simulateur.")