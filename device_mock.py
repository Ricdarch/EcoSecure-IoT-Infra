import random
import time
import json

class SmartPlug:
    def __init__(self, id, plug_time, connected, energy_consumption, is_used, idle_time):
        self.id = id
        self.plug_time = plug_time
        self.connected = connected
        self.energy_consumption = energy_consumption
        self.is_used = is_used
        self.idle_time = idle_time

    def generate_data(self):
        self.plug_time = random.uniform(min, max)
    