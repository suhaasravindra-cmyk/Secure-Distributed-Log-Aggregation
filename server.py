import socket
import ssl
import threading
import json
import os
import sys
from datetime import datetime

# ================= Configuration =================
HOST = '0.0.0.0'
PORT = 8443
CERT_FILE = './certs/cert.pem'
KEY_FILE = './certs/key.pem'
LOG_STORE = 'centralized_logs.txt'

# Lock for thread-safe file writing
file_lock = threading.Lock()
# =================================================

def process_log(log_data):
    """Parses JSON log data, extracts metadata, and writes to the centralized store safely."""
    try:
        log_json = json.loads(log_data)
        timestamp = log_json.get("timestamp", datetime.utcnow().isoformat())
        level = log_json.get("level", "UNKNOWN")
        source = log_json.get("source", "Unknown_Machine")
        message = log_json.get("message", "")
        
        # Format the log for storage
        formatted_log = f"[{timestamp}] [{level}] [{source}] : {message}\n"
        
        # Thread-safe write to centralized log store
        with file_lock:
            with open(LOG_STORE, "a") as f:
                f.write(formatted_log)
        
        print(f"[AGGREGATED] {formatted_log.strip()}")
    except json.JSONDecodeError:
        print(f"[FORMAT ERROR] Failed to decode incoming log: {log_data}")
    except Exception as e:
        print(f"[PROCESSING ERROR] {e}")

def handle_client(secure_conn, addr):
    """Handles an individual client's secure socket connection concurrently."""
    print(f"[NEW CONNECTION] {addr} connected securely.")
    try:
        while True:
            # Receive data in 1024 byte chunks over the low-level socket
            data = secure_conn.recv(1024)
            if not data:
                break # Client disconnected gracefully
            
            # Decode bytes to string and process
            process_log(data.decode('utf-8'))
            
    except ssl.SSLError as e:
        print(f"[SSL ERROR] Handshake or protocol failure with {addr} - {e}")
    except ConnectionResetError:
        print(f"[DISCONNECTED] {addr} closed the connection abruptly.")
    except Exception as e:
        print(f"[CONNECTION ERROR] Error handling {addr} - {e}")
    finally:
        secure_conn.close()
        print(f"[CLOSED] Connection with {addr} has been safely closed.")

def start_server():
    """Initializes the low-level TCP socket, wraps it in TLS, and listens for clients."""
    
    # 1. Verify SSL certificates exist before starting
    if not os.path.exists(CERT_FILE) or not os.path.exists(KEY_FILE):
        print("[FATAL ERROR] SSL certificates missing. Run the OpenSSL command in the README.")
        sys.exit(1)

    # 2. Ensure log store file exists
    if not os.path.exists(LOG_STORE):
        open(LOG_STORE, 'w').close()

    # 3. Create Low-level TCP Socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(10) # Backlog of 10 connections for backpressure handling
    except Exception as e:
        print(f"[BIND ERROR] Failed to bind to {HOST}:{PORT} - {e}")
        sys.exit(1)

    # 4. Setup SSL/TLS Context
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)

    print(f"[STARTING] Central Collector listening securely on port {PORT}...")

    try:
        while True:
            # Accept incoming raw connection
            client_socket, addr = server_socket.accept()
            
            try:
                # 5. Wrap the raw socket with TLS
                secure_conn = context.wrap_socket(client_socket, server_side=True)
                
                # 6. Spawn a new thread to handle this concurrent client
                thread = threading.Thread(target=handle_client, args=(secure_conn, addr))
                thread.daemon = True # Allows thread to exit when main program exits
                thread.start()
                
                print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
            except ssl.SSLError as e:
                print(f"[SSL REJECTED] Failed to establish secure connection with {addr} - {e}")
                client_socket.close()
                
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Server shutting down gracefully via Keyboard Interrupt.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()