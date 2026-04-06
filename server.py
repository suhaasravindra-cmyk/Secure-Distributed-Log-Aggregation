import socket
import csv
import os
from datetime import datetime

HOST = "0.0.0.0"
PORT = 9999
CSV_FILE = "logs.csv"

# Create CSV with header if not exists
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp", "level", "message"])

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((HOST, PORT))

print(f"[SERVER STARTED] Listening on {PORT}...")

while True:
    data, addr = server.recvfrom(1024)
    log = data.decode()

    try:
        timestamp, level, message = log.split(",", 2)

        # Save to CSV
        with open(CSV_FILE, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, level, message])

        print(f"[RECEIVED] {addr} → {log}")

    except Exception as e:
        print(f"[ERROR PARSING] {e}")