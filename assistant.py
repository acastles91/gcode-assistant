import os
import re
import subprocess
import keyboard

slave1_ip = "192.168.178.125"
slave2_ip = "192.168.178.150"
slave1_file = "slave-1.gcode"
slave2_file = "slave-2.gcode"
master_file = "master-loop.gcode"

class GCodeController:
    def __init__(self, master_file, slave1_file, slave2_file, slave1_ip, slave2_ip):
        self.master_file = master_file
        self.slave1_file = slave1_file
        self.slave2_file = slave2_file
        self.slave1_ip = slave1_ip
        self.slave2_ip = slave2_ip
        self.index = 0
        self.master_position = "G0 X0 Y0 Z0"
        self.slave1_position = "G0 X0 Y0 Z0"
        self.slave2_position = "G0 X0 Y0 Z0"

    def is_valid_gcode(self, line):
        return line.strip().startswith("G0")

    def get_filtered_gcode(self, file_name):
        file_path = os.path.join('gcode_files', file_name)
        with open(file_path, 'r') as file:
            valid_lines = [line.strip() for line in file if self.is_valid_gcode(line)]
        return valid_lines

    def send_curl(self, ip, gcode):
        curl_command = [
            'curl',
            '-H', 'Content-Type: application/json',
            '-X', 'POST',
            f'http://{ip}:7125/printer/gcode/script',
            '-d', f'{{"script":"{gcode}"}}'
        ]
        result = subprocess.run(curl_command, capture_output=True, text=True)
        return result

    def send_gcode_command(self, master_gcode, slave1_gcode, slave2_gcode):
        print(f"Sending to Master: {master_gcode}")
        self.send_curl('localhost', master_gcode)
        print(f"Sending to Slave 1: {slave1_gcode}")
        self.send_curl(self.slave1_ip, slave1_gcode)
        print(f"Sending to Slave 2: {slave2_gcode}")
        self.send_curl(self.slave2_ip, slave2_gcode)

    def go_next_position(self):
        master_lines = self.get_filtered_gcode(self.master_file)
        slave1_lines = self.get_filtered_gcode(self.slave1_file)
        slave2_lines = self.get_filtered_gcode(self.slave2_file)

        if self.index < min(len(master_lines), len(slave1_lines), len(slave2_lines)):
            self.master_position = master_lines[self.index]
            self.slave1_position = slave1_lines[self.index]
            self.slave2_position = slave2_lines[self.index]
            self.send_gcode_command(self.master_position, self.slave1_position, self.slave2_position)
            self.index += 1
            print(f"Current positions - Master: {self.master_position}, Slave 1: {self.slave1_position}, Slave 2: {self.slave2_position}")
        else:
            print("Reached the end of G-code files.")

    def go_previous_position(self):
        if self.index > 0:
            self.index -= 1
            inverted_master = self.invert_gcode(self.master_position)
            inverted_slave1 = self.invert_gcode(self.slave1_position)
            inverted_slave2 = self.invert_gcode(self.slave2_position)
            self.send_gcode_command(inverted_master, inverted_slave1, inverted_slave2)
            print(f"Moved to previous positions - Master: {inverted_master}, Slave 1: {inverted_slave1}, Slave 2: {inverted_slave2}")
        else:
            print("Already at the starting position.")

    def invert_gcode(self, gcode):
        coord_pattern = re.compile(r'([XYZ])(-?\d+(\.\d+)?)')
        coords = coord_pattern.findall(gcode)
        inverted_coords = [f"{axis}{-float(value)}" for axis, value, _ in coords]
        return "G0 " + " ".join(inverted_coords)

def run_interactive_control(master_file, slave1_file, slave2_file, slave1_ip, slave2_ip):
    controller = GCodeController(master_file, slave1_file, slave2_file, slave1_ip, slave2_ip)
    
    print("Interactive G-code Controller")
    print("Press 'n' to move to the next position")
    print("Press 'p' to move to the previous position")
    print("Press 'q' to quit")

    def on_key_press(event):
        if event.name == 'n':
            controller.go_next_position()
        elif event.name == 'p':
            controller.go_previous_position()
        elif event.name == 'q':
            print("Quitting...")
            keyboard.unhook_all()

    keyboard.on_press(on_key_press)

    keyboard.wait('q')

# To use in the interpreter:
# run_interactive_control('master_file.gcode', 'slave_file.gcode', '192.168.1.100')
# run_interactive_control('master_file', 'slave1_file', slave2_file', 'slave1_ip', 'slave2_ip')
