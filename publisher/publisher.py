import random
import time
import json
import paho.mqtt.client as mqtt

# --- HARDWARE LAYER: THE POWER DISTRIBUTION UNIT ---

class SmartPDU:
    def __init__(self, config):
        self.id = config["id"]
        self.role = config.get("role", "primary")  # primary / backup
        self.location = config["location"]
        
        # Physical State
        self.pdu_temp = 25.0
        self.fan_speed = 20.0  # Rotation speed in %
        self.current_power = 0.0
        self.workload_limit = 1.0  # 1.0 = 100% capacity
        
        # Logic State
        self.status = "ONLINE"
        self.is_running = True

    def update_physics(self, room_temp):
        """ Calculates the thermal evolution of the PDU """
        if not self.is_running:
            # Passive cooling if unit is OFF
            self.pdu_temp -= (self.pdu_temp - room_temp) * 0.05
            self.current_power = 0
            self.fan_speed = 0
            return

        # 1. Fan Management (Dynamic PWM)
        if self.pdu_temp > 45:
            # Linear acceleration between 45°C and 75°C
            self.fan_speed = min(100, 20 + (self.pdu_temp - 45) * 2.6)
        else:
            self.fan_speed = 20

        # 2. Heat Generation vs. Cooling Efficiency
        # Heat increases with power consumption
        heat_gen = (self.current_power / 1000) * 0.6
        # Cooling depends on fan speed and the delta between PDU and room temp
        cooling = (self.fan_speed / 100) * (self.pdu_temp - room_temp) * 0.15
        
        self.pdu_temp += (heat_gen - cooling)

        # 3. Safety Logic (Thresholds)
        if self.pdu_temp >= 80:
            self.status = "EMERGENCY_SHUTDOWN"
            self.is_running = False
            self.current_power = 0
        elif self.pdu_temp >= 70:
            self.status = "CRITICAL_THROTTLING"
            self.workload_limit = 0.5  # Throttling to 50%
        elif self.pdu_temp >= 60:
            self.status = "WARNING_ORANGE"
            self.workload_limit = 1.0
        else:
            self.status = "ONLINE"
            self.workload_limit = 1.0

    def set_load(self, base_power):
        """ Defines consumption based on Datacenter demand """
        if self.is_running:
            # Actual power is capped by safety throttling
            self.current_power = base_power * self.workload_limit

# --- ORCHESTRATION LAYER: THE DATACENTER ---

class Datacenter:
    def __init__(self):
        self.room_temp = 22.0
        self.target_temp = 22.0
        self.pdus = []
        
    def add_pdu(self, pdu):
        self.pdus.append(pdu)

    def manage_failover(self):
        """ Ops Logic: If a primary unit fails, the backup takes over """
        for pdu in self.pdus:
            if pdu.role == "primary":
                # Find the backup partner (same rack location)
                backup = next((p for p in self.pdus if p.role == "backup" and p.location == pdu.location), None)
                
                if not pdu.is_running and backup:
                    backup.set_load(2500)  # Backup takes the 2500W load
                elif pdu.is_running:
                    pdu.set_load(2500)     # Primary runs normally
                    if backup: backup.set_load(50)  # Backup stays in standby

    def update_environment(self):
        """ PDU heat warms up the room, HVAC cools it back down """
        total_heat_waste = sum(p.current_power for p in self.pdus) / 10000
        self.room_temp += total_heat_waste
        # Simulation of the HVAC system struggling to maintain 22°C
        self.room_temp -= (self.room_temp - self.target_temp) * 0.1

# --- MAIN EXECUTION ---

def main():
    # 1. Initialization (Simulated JSON config)
    dc = Datacenter()
    configs = [
        {"id": "PDU-01-A", "location": "Rack-1", "role": "primary"},
        {"id": "PDU-01-B", "location": "Rack-1", "role": "backup"},
        {"id": "PDU-02-A", "location": "Rack-2", "role": "primary"},
        {"id": "PDU-02-B", "location": "Rack-2", "role": "backup"}
    ]
    for cfg in configs:
        dc.add_pdu(SmartPDU(cfg))

    # 2. MQTT Configuration
    client = mqtt.Client()
    # client.connect("your_broker_address", 1883)

    print("--- Starting Datacenter Simulator (Ops Mode) ---")
    
    try:
        while True:
            dc.manage_failover()
            dc.update_environment()
            
            for pdu in dc.pdus:
                pdu.update_physics(dc.room_temp)
                
                # Payload Generation
                topic = f"datacenter/{pdu.location}/{pdu.id}".lower()
                payload = json.dumps({
                    "status": pdu.status,
                    "temp_c": round(pdu.pdu_temp, 1),
                    "power_w": round(pdu.current_power, 0),
                    "fan_speed_pct": round(pdu.fan_speed, 0),
                    "ambient_temp_c": round(dc.room_temp, 1)
                })
                # client.publish(topic, payload)
                
                # Console Monitoring
                if pdu.role == "backup" and pdu.current_power > 100:
                    print(f"[ALERT] Backup unit {pdu.id} is ACTIVE! Temp: {pdu.pdu_temp}C")
                if pdu.status == "EMERGENCY_SHUTDOWN":
                    print(f"[CRITICAL] Unit {pdu.id} has SHUT DOWN due to overheating!")

            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nSimulator stopped by user.")

if __name__ == "__main__":
    main()