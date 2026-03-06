import serial
import json
import os
import time

config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config", "cpflight.json"))
with open(config_path, "r") as f:
    config = json.load(f)

USB_PORT = config.get("USB", "COM3")  # example "COM3" 
USB_BAUD = config.get("BAUD", 115200)  # default baudrate

if not USB_PORT:
    raise ValueError("USB port not found in config/cpflight.json")

try:
    ser = serial.Serial(USB_PORT, USB_BAUD, timeout=0.5)
    print(f"Connected to CPFlight FCU via USB at {USB_PORT} ({USB_BAUD} baud)")

    while True:
        try:
            user_input = input("Send command: ").strip()
        except KeyboardInterrupt:
            print("\nInterrupted by user (Ctrl+C). Exiting...")
            break

        if user_input.lower() in ("exit", "off"):
            print("Exit command received. Closing connection...")
            break

        if user_input:
            cmd = (user_input + "\n").encode()
            ser.write(cmd)
            print("Sent:", user_input)

            # Try to read 
            time.sleep(0.05)  # small delay
            if ser.in_waiting:
                resp = ser.read(ser.in_waiting).decode(errors="ignore")
                print("Received:", resp)

except Exception as e:
    print("Connection error:", e)

finally:
    try:
        ser.write(b"K999\n")
    except Exception:
        pass
    ser.close()
    print("Connection closed.")
