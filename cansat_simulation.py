import serial
from datetime import datetime, timedelta
import time
import random

# Load constants based on year
def load_constants(year):
    constants = {
        2025: {
            "TEAM_ID": "1000",
            "PACKET_COUNT_START": 0,
            "START_TIME": datetime(2025, 11, 14, 13, 0, 0),
            "STATES": ["LAUNCH_PAD", "ASCENT", "APOGEE", "DESCENT", "PROBE_RELEASE", "LANDED"],
            "altitude_values": {
                "LAUNCH_PAD": (0, 0.1),
                "ASCENT": (10, 1000),
                "APOGEE": (1000, 1100),
                "DESCENT": (500, 1000),
                "PROBE_RELEASE": (50, 500),
                "LANDED": (0, 0.1)
            },
            "temperature_range": (-5.0, 35.0),
            "pressure_range": (80.0, 120.0),
            "voltage_range": (3.5, 4.2),
            "gyro_range": (-5.0, 5.0),
            "accel_range": (-2.0, 2.0),
            "mag_range": (-1.0, 1.0),
            "rotation_rate_range": (0, 360),
            "gps_altitude_range": (0, 1000),
            "latitude_range": (-90.0, 90.0),
            "longitude_range": (-180.0, 180.0),
            "gps_sats_range": (3, 12),
            "commands": ["CXON", "CAL", "FLY"]
        }
    }
    return constants.get(year, constants[2025])

class CanSatSimulator:
    command = ""
    flight_mode = False
    def __init__(self, year, comport, baudrate, transmit_delim="\n", receive_delim="\n"):
        self.constants = load_constants(year)
        self.serial_port = serial.Serial(comport, baudrate, timeout=1)
        self.transmit_delim = transmit_delim
        self.receive_delim = receive_delim
        self.telemetry_on = False
        self.simulation_mode = False
        self.packet_count = self.constants["PACKET_COUNT_START"]
        self.state = "LAUNCH_PAD"
        self.last_transmission_time = datetime.now()  # Track the last transmission time
        print(f"CanSat Simulator initialized for year {year} on {comport} at {baudrate} baud.")

    def send_command(self, command):
        """Send a command to the CanSat."""
        self.serial_port.write((command + self.transmit_delim).encode())
        print(f"Sent: {command}")

    def receive_data(self):
        """Receive data from the CanSat."""
        if self.serial_port.in_waiting > 0:
            data = self.serial_port.readline().decode().strip()
            if data:
                print(f"Received: {data}")
                self.process_command(data)

    def process_command(self, data):
        """Process incoming commands and handle specific actions."""
        parts = data.split(",")
        if len(parts) < 4:
            print("Invalid command format")
            return

        command_type = parts[2]
        self.command = ''.join(parts[2:])
        if command_type == "CX":
            self.handle_cx(parts[3])
        elif command_type == "FLY":
            if(parts[3] == "GO"):
                self.handle_fly()
        elif command_type == "ST":
            self.handle_st(parts[3])
        elif command_type == "SIM":
            self.handle_sim(parts[3])
        elif command_type == "CAL":
            self.handle_cal()
        elif command_type == "MEC":
            self.handle_mec(parts[3], parts[4])

    def handle_cx(self, on_off):
        """Turn telemetry on or off."""
        if on_off == "ON":
            self.telemetry_on = True
            print("Telemetry transmission activated.")
        elif on_off == "OFF":
            self.telemetry_on = False
            print("Telemetry transmission deactivated.")

    def handle_fly(self):
        """Start flight and change state from LAUNCH_PAD."""
        if self.telemetry_on:
            self.flight_mode = True
            self.packet_count = 0
            print("Flight command received. State changed overtime.")
    
    def buatcs(self, data_str):
        hasil = 0
        for char in data_str[:150]:  # Process up to 150 characters
            hasil += ord(char)  # Add ASCII value of each character
            if char == '\0':    # Stop if a null character is encountered
                break
        return hasil & 0xFFFF  # Return as a 16-bit result
    
    def transmit_telemetry(self):
        """Transmit telemetry data based on the current state every 1 second."""
        current_time = datetime.now()
        if (current_time - self.last_transmission_time).total_seconds() >= 1:
            format_time = current_time.strftime("%H:%M:%S")
            gps_time = format_time
            if self.flight_mode:
                if(self.state == "LANDED"):
                    self.flight_mode = False
                    self.packet_count = 0
                    print("Flight has ended.")
                    print("State changed to LAUNCH_PAD.")
                print("Changing State")
                self.state = self.constants["STATES"][min(self.packet_count // 10, len(self.constants["STATES"]) - 1)]

            packet = f"{self.constants['TEAM_ID']},{self.packet_count},{format_time},{self.state}," \
                     f"{round(random.uniform(*self.constants['altitude_values'][self.state]), 1)}," \
                     f"{round(random.uniform(*self.constants['temperature_range']), 2)}," \
                     f"{round(random.uniform(*self.constants['pressure_range']), 1)}," \
                     f"{round(random.uniform(*self.constants['voltage_range']), 2)}," \
                     f"{round(random.uniform(*self.constants['gyro_range']), 2)}," \
                     f"{round(random.uniform(*self.constants['gyro_range']), 2)}," \
                     f"{round(random.uniform(*self.constants['gyro_range']), 2)}," \
                     f"{round(random.uniform(*self.constants['accel_range']), 2)}," \
                     f"{round(random.uniform(*self.constants['accel_range']), 2)}," \
                     f"{round(random.uniform(*self.constants['accel_range']), 2)}," \
                     f"{round(random.uniform(*self.constants['mag_range']), 2)}," \
                     f"{round(random.uniform(*self.constants['mag_range']), 2)}," \
                     f"{round(random.uniform(*self.constants['mag_range']), 2)}," \
                     f"{random.randint(*self.constants['rotation_rate_range'])}," \
                     f"{gps_time}," \
                     f"{round(random.uniform(*self.constants['gps_altitude_range']), 2)}," \
                     f"{round(random.uniform(*self.constants['latitude_range']), 2)}," \
                     f"{round(random.uniform(*self.constants['longitude_range']), 2)}," \
                     f"{random.randint(*self.constants['gps_sats_range'])}," \
                     f"{self.command},," \

            cst = self.buatcs(packet)
            cs1 = cst & 0xFF
            cs2 = (cst >> 8) & 0xFF
            checksum = ~(cs1 + cs2) & 0xFF         
            packet += f"{checksum}"
            print(f"Transmitting telemetry: {packet} Checksum: {checksum}")
            self.serial_port.write((packet + self.transmit_delim).encode())
            self.packet_count += 1
            self.last_transmission_time = current_time

    def handle_st(self, time_value):
        """Set the CanSat's time."""
        if time_value == "GPS":
            mission_time = datetime.now().time()
        else:
            mission_time = datetime.strptime(time_value, "%H:%M:%S").time()
        print(f"Mission time set to: {mission_time}")

    def handle_sim(self, mode):
        """Enable, activate, or disable simulation mode."""
        if mode == "ENABLE":
            self.simulation_mode = True
            print("Simulation mode enabled.")
        elif mode == "ACTIVATE" and self.simulation_mode:
            print("Simulation mode activated.")
        elif mode == "DISABLE":
            self.simulation_mode = False
            print("Simulation mode disabled.")

    def handle_cal(self):
        """Calibrate altitude to zero."""
        self.packet_count = 0
        print("Altitude calibrated to zero.")

    def handle_mec(self, device, on_off):
        """Activate or deactivate a specific mechanism."""
        if on_off == "ON":
            print(f"Mechanism {device} activated.")
        elif on_off == "OFF":
            print(f"Mechanism {device} deactivated.")

    def start(self):
        """Main loop for receiving data and transmitting telemetry if enabled."""
        try:
            while True:
                self.receive_data()
                if self.telemetry_on:
                    self.transmit_telemetry()
                time.sleep(0.1)  # Short delay to avoid CPU overload
        except KeyboardInterrupt:
            print("Simulation terminated.")
        finally:
            self.serial_port.close()

# Example usage:
year = 2025
comport = "COM1"  # Replace with actual COM port
baudrate = 19200
transmit_delim = "\r"
receive_delim = "\r"

cansat = CanSatSimulator(year, comport, baudrate, transmit_delim, receive_delim)
cansat.start()
