import socket
import json
import os

config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config", "cpflight.json"))
with open(config_path, "r") as f:
    config = json.load(f)

FCU_IP = config.get("IP")
FCU_PORT = config.get("PORT")

if not FCU_IP or not FCU_PORT:
    raise ValueError("IP or PORT not found in config/cpflight.json")

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((FCU_IP, FCU_PORT))
    print(f"Connected to CPFlight FCU at {FCU_IP}:{FCU_PORT}")

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
            sock.sendall((user_input + "\n").encode())
            print("Sent:", user_input)

except Exception as e:
    print("Connection error:", e)

finally:
    try:
        sock.sendall(b"K999\n")
    except Exception:
        pass
    sock.close()
    print("Connection closed.")
