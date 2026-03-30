import socket
import ssl
import json
import time
import random
from datetime import datetime, timezone

def generate_log_json(level, machine_id, message):
    """
    Creates a structured JSON log entry. 
    Using JSON makes the logs easy to parse for databases like Elasticsearch or MongoDB.
    """
    return json.dumps({
        # Generate an ISO 8601 timestamp in UTC format (e.g., 2023-10-27T10:00:00Z)
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "level": level,
        "source": machine_id,
        "message": message
    })

def run_client(server_ip, machine_id):
    PORT = 8443
    
    # 1. Create a standard TCP socket (IPv4, Stream-based)
    # This is the "raw" connection before any encryption is added.
    raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # 2. Set up SSL context
    # We use 'create_default_context' which is pre-configured with secure defaults.
    context = ssl.create_default_context()
    
    # Since we are using a Self-Signed Certificate (generated via OpenSSL), 
    # we tell the client to skip hostname and certificate validation. 
    # (Note: In a production environment, you would point this to your Root CA).
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    # 3. Wrap the raw socket with SSL/TLS
    # This upgrades the connection to an encrypted tunnel.
    secure_socket = context.wrap_socket(raw_socket, server_hostname=server_ip)

    try:
        print(f"[{machine_id}] Connecting securely to {server_ip}:{PORT}...")
        
        # Initiate the connection and the TLS Handshake
        secure_socket.connect((server_ip, PORT))
        print(f"[{machine_id}] TLS connection established successfully.")

        # --- 4. Push Model: Weighted Random Event Generator ---
        # This simulates a real machine generating different types of logs over time.
        print(f"[{machine_id}] Starting Realistic Event Generator (Ctrl+C to stop)...")
        
        while True:
            # SIMULATION LOGIC: Use 'random.choices' to control frequency.
            # We want mostly INFO logs (85%), some WARNINGS (12%), and very few ERRORS (3%).
            event_level = random.choices(
                population=["INFO", "WARNING", "ERROR"],
                weights=[85, 12, 3],
                k=1
            )[0]
            
            # Map the event level to a realistic system message
            messages = {
                "INFO": "System heartbeat check - Active",
                "WARNING": "Memory usage slightly elevated (78%).",
                "ERROR": "Critical: Database connection dropped!"
            }
            
            # Create the JSON payload
            log_json = generate_log_json(event_level, machine_id, messages[event_level])
            
            # Send the log as UTF-8 encoded bytes over the encrypted socket
            # 'sendall' ensures the entire message is transmitted.
            secure_socket.sendall(log_json.encode('utf-8'))
            
            print(f"[{machine_id} SENT] {event_level}: {messages[event_level]}")
            
            # Wait 5 seconds between logs to avoid flooding the server 
            # and to simulate standard telemetry intervals.
            time.sleep(5) 

    except KeyboardInterrupt:
        print(f"\n[{machine_id}] User stopped the generator.")
    except Exception as e:
        print(f"[{machine_id}] Connection Error: {e}")
    finally:
        # 5. Essential cleanup: Close the socket to free up the system port
        print(f"[{machine_id}] Closing secure connection.")
        secure_socket.close()

if __name__ == "__main__":
    import sys
    # Ensure the user provides the Server IP and a unique Name for this machine
    if len(sys.argv) < 3:
        print("Usage: python client.py <server_ip> <machine_id>")
    else:
        run_client(sys.argv[1], sys.argv[2])