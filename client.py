import socket
import ssl
import json
import time
import random
from datetime import datetime, timezone

def generate_log_json(level, machine_id, message):
    """Generates a structured JSON log entry with a clean UTC timestamp."""
    return json.dumps({
        # Modern UTC timestamp (ISO 8601)
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "level": level,
        "source": machine_id,
        "message": message
    })

def run_client(server_ip, machine_id):
    PORT = 8443
    
    # 1. Create a standard TCP socket (Low-level networking)
    raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # 2. Set up SSL context (Mandatory Security)
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    # 3. Wrap the socket with SSL/TLS
    secure_socket = context.wrap_socket(raw_socket, server_hostname=server_ip)

    try:
        print(f"[{machine_id}] Connecting securely to {server_ip}:{PORT}...")
        secure_socket.connect((server_ip, PORT))
        print(f"[{machine_id}] TLS connection established successfully.")

        # --- 4. Push Model: Weighted Random Event Generator ---
        print(f"[{machine_id}] Starting Realistic Event Generator (Ctrl+C to stop)...")
        
        while True:
            # WEIGHTS: INFO (85%), WARNING (12%), ERROR (3%)
            # This simulates a healthy system where errors are rare anomalies.
            event_level = random.choices(
                population=["INFO", "WARNING", "ERROR"],
                weights=[85, 12, 3],
                k=1
            )[0]
            
            # Context-aware messages based on the chosen level
            messages = {
                "INFO": "System heartbeat check - Active",
                "WARNING": "Memory usage slightly elevated (78%).",
                "ERROR": "Critical: Database connection dropped!"
            }
            
            # Generate the structured JSON log
            log_json = generate_log_json(event_level, machine_id, messages[event_level])
            
            # Send raw bytes over the secure encrypted socket
            secure_socket.sendall(log_json.encode('utf-8'))
            
            print(f"[{machine_id} SENT] {event_level}: {messages[event_level]}")
            
            # Wait 5 seconds before the next event to simulate telemetry intervals
            time.sleep(5) 

    except KeyboardInterrupt:
        print(f"\n[{machine_id}] User stopped the generator.")
    except Exception as e:
        print(f"[{machine_id}] Connection Error: {e}")
    finally:
        # Essential cleanup: Ensure the encrypted tunnel is closed safely
        print(f"[{machine_id}] Closing secure connection.")
        secure_socket.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python client.py <server_ip> <machine_id>")
    else:
        run_client(sys.argv[1], sys.argv[2])