import os
import serial
import time
import argparse
import sys
import fcntl

class ZigbeeModuleChecker:
    def __init__(self, port, baudrate=115200, timeout=1, custom_command=None, debug=False):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.custom_command = custom_command
        self.debug = debug

    def get_process_name_by_pid(self, pid):
        """Get the process name by PID."""
        try:
            process_info = os.popen(f"ps -p {pid} -o comm=").read().strip()
            return process_info
        except Exception as e:
            return None

    def check_port_availability(self):
        """Check if the serial port is available for communication using fuser."""
        try:
            fuser_output = os.popen(f"fuser {self.port}").read().strip()
            if fuser_output:
                pids = fuser_output.split()
                process_names = [self.get_process_name_by_pid(pid) for pid in pids]
                process_names = list(filter(None, process_names))  # Remove any None values

                # Unified and compact output
                print(f"The port {self.port} is occupied by process ID(s): {', '.join(pids)} ({', '.join(process_names)})")

                # If node is present, suggest stopping zigbee2mqtt
                if 'node' in process_names:
                    print("The process 'node' is running on the port and might be related to zigbee2mqtt.")
                    print("Please try stopping the zigbee2mqtt service using: systemctl stop zigbee2mqtt")
                else:
                    print("Please stop the process or release the port manually.")

                return False  # Port is occupied
            return True  # Port is free
        except Exception as e:
            print(f"Error checking port availability: {e}")
            return False


    def send_command(self, command):
        """Send command and wait for response."""
        try:
            with serial.Serial(self.port, self.baudrate, timeout=self.timeout) as ser:
                fcntl.flock(ser.fileno(), fcntl.LOCK_EX)  # Lock the port
                ser.reset_input_buffer()

                if self.debug:
                    print(f"Sending command: {command.hex()}")  # Debugging line to print command

                ser.write(command)
                time.sleep(0.5)
                response = ser.read(ser.in_waiting or 64)

                if not response:
                    print("No response received. The module might not be working.")
                else:
                    return response
        except serial.SerialException as e:
            print(f"Error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

    def process_version_response(self, response):
        """Parse and display the SYS Version response."""
        if self.debug:
            print(f"Raw response received: {response.hex()}")  # Debugging line to print raw response

        if not response:
            print("No response received.")
            return

        # Check if the response starts with known prefixes for CC2652, CC2530, and CC2538
        if response.startswith(b'\xFE\x0A\x61\x02'):
            self.process_version(response, "CC2652")
        elif response.startswith(b'\xFE\x0E\x61\x02'):
            self.process_version(response, "CC2530")
        elif response.startswith(b'\xFE\x10\x61\x02'):
            self.process_version(response, "CC2538")
        else:
            print("Unknown chip detected. Skipping specialized parsing.")
            print(f"Raw response: {response.hex()}")

        # After processing, check for remaining bytes (asynchronous data)
        if len(response) > 14:  # assuming version data is 14 bytes long
            async_data = response[14:]
            print("Additional asynchronous data detected. Skipping:")
            print(f"Raw data: {async_data.hex()}")

    def process_version(self, response, chip_type):
        """Parse and display the SYS Version response for the given Zigbee chip type."""
        if self.debug:
            print(f"Parsing response: {response.hex()}")  # Debugging line to print response being parsed

        try:
            transport_version = response[4]
            product_id = response[5]
            major_release = response[6]
            minor_release = response[7]
            maintenance_release = response[8]
            revision = response[9:14]

            # Output the parsed version information with chip type
            print(f"SYS Version response detected for {chip_type}:")
            print(f"Transport Version: {transport_version}")
            print(f"Product ID: {product_id} — {chip_type} Zigbee Module.")
            print(f"Major Release: {major_release}")
            print(f"Minor Release: {minor_release}")
            print(f"Maintenance Release: {maintenance_release}")
            print(f"Stack Version: {major_release}.{minor_release}.{maintenance_release} — Indicates Z-Stack compatibility.")
            print(f"Revision: {revision.hex()} — Firmware Revision Details.")
        except Exception as e:
            print(f"Error while parsing the response: {e}")

    def check(self):
        """Check the port, send version command and process the response."""
        if not self.check_port_availability():
            sys.exit(1)  # Exit the script if the port is busy

        # Send version command
        version_command = b'\xFE\x00\x21\x02\x23'
        response = self.send_command(version_command)

        if response:
            self.process_version_response(response)

def main():
    parser = argparse.ArgumentParser(
        description="Check the version, reset or send custom command to the CC2652P, CC2530, or CC2538 Zigbee module over UART."
    )
    parser.add_argument(
        "port",
        type=str,
        help="Serial port where the Zigbee module is connected (e.g., /dev/ttyMOD4).",
    )
    parser.add_argument(
        "--baudrate",
        type=int,
        default=115200,
        help="Baud rate for serial communication (default: 115200).",
    )
    # Adding short flags for reset and version commands
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Send reset command to the module.",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Send version request to the module.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=1,
        help="Timeout for waiting for a response (in seconds, default: 1)."
    )
    parser.add_argument(
        "--custom-command",
        type=str,
        help="Send a custom command to the module in hex format (e.g., 'fe01210100')."
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output."
    )

    args = parser.parse_args()

    checker = ZigbeeModuleChecker(args.port, args.baudrate, args.timeout, args.custom_command, args.debug)

    # Reset or version command
    if args.reset:
        print("Sending reset command...")
        checker.check()
    elif args.version or not args.reset:
        checker.check()


if __name__ == "__main__":
    main()
