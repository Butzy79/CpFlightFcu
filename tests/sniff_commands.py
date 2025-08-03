import json
import os
from scapy.all import sniff, IP, TCP, Raw, conf

config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config", "cpflight.json"))
with open(config_path, "r") as f:
    config = json.load(f)

target_ip = config.get("IP")
if not target_ip:
    raise ValueError("Ip not found in config/cpflight.json")

conf.use_pcap = True
def packet_callback(packet):
    if packet.haslayer(IP) and packet.haslayer(TCP) and packet.haslayer(Raw):
        if target_ip in (packet[IP].src, packet[IP].dst):
            try:
                data_bytes = packet[Raw].load
                hex_str = " ".join(f"{b:02x}" for b in data_bytes)
                ascii_str = "".join(chr(b) if 32 <= b <= 126 else "." for b in data_bytes)
                print(f"Raw data (hex): {hex_str} (ascii): {ascii_str}")
            except UnicodeDecodeError:
                pass

INTERFACE = "Ethernet"
FILTRO = f"tcp and host {target_ip}"

print(f"[*] Sniffing {INTERFACE} to IP target {target_ip}")
sniff(filter=FILTRO, iface=INTERFACE, prn=packet_callback, store=False)
