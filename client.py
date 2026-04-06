import socket
import time
import random

SERVER_IP = "127.0.0.1"
PORT = 9999

logs = [
    ("INFO", "User logged in"),
    ("ERROR", "Disk full"),
    ("WARNING", "CPU usage high"),
    ("INFO", "Request processed"),
    ("ERROR", "Connection timeout")
]

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    level, message = random.choice(logs)
    timestamp = time.strftime("%H:%M:%S")

    log = f"{timestamp},{level},{message}"
    client.sendto(log.encode(), (SERVER_IP, PORT))

    print(f"Sent: {log}")
    time.sleep(1)