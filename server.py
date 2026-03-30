import socket
import ssl
import threading
import json
import os
import sys
from datetime import datetime

# ================= Configuration =================
HOST = '0.0.0.0'       # Listen on all available network interfaces
PORT = 8443            # Standard port for secure data transfer
CERT_FILE = './certs/cert.pem'  # Path to the public SSL certificate
KEY_FILE = './certs/key.pem'    # Path to the private RSA key
LOG_STORE = 'centralized_logs.txt' # The file where all logs are aggregated

# Threading Lock ensures that only one thread can write to the file at a time,
# preventing data corruption or scrambled text in the log file.
file_lock = threading.Lock()
# =================================================

def process_log(log_data):
    """
    Parses JSON log data, extracts metadata, and writes to the centralized store safely.
    This acts as the 'Data Processing' layer of the server.
    """
    try:
        # Step 1: Deserialize the incoming byte-string into a JSON object (dictionary)
        log_json = json.loads(log_data)
        
        # Step 2: Extract specific fields with fallback defaults if keys are missing
        timestamp = log_json.get("timestamp", datetime.utcnow().isoformat())
        level = log_json.get("level", "UNKNOWN")
        source = log_json.get("source", "Unknown_Machine")
        message = log_json.get("message", "")
        
        # Step 3: Format the log entry into a human-readable string
        formatted_log = f"[{timestamp}] [{level}] [{source}] : {message}\n"
        
        # Step 4: Write to file using a context manager and the threading lock
        with file_lock:
            with open(LOG_STORE, "a") as f:
                f.write(formatted_log)
        
        # Step 5: Mirror the output to the server console for real-time monitoring
        print(f"[AGGREGATED] {formatted_log.strip()}")

    except json.JSONDecodeError:
        print(f"[FORMAT ERROR] Failed to decode incoming log: {log_data}")
    except Exception as e:
        print(f"[PROCESSING ERROR] {e}")

def handle_client(secure_conn, addr):
    """
    Handles an individual client's secure socket connection concurrently.
    This function runs in a separate thread for every connected agent.
    """
    print(f"[NEW CONNECTION] {addr} connected securely.")
    try:
        while True:
            # Receive data in 1024-byte chunks (buffer size)
            data = secure_conn.recv(1024)
            
            if not data:
                # If no data is received, the client has closed the connection
                break 
            
            # Decode the encrypted bytes to a UTF-8 string and process them
            process_log(data.decode('utf-8'))
            
    except ssl.SSLError as e:
        print(f"[SSL ERROR] Handshake or protocol failure with {addr} - {e}")
    except ConnectionResetError:
        print(f"[DISCONNECTED] {addr} closed the connection abruptly.")
    except Exception as e:
        print(f"[CONNECTION ERROR] Error handling {addr} - {e}")
    finally:
        # Always close the connection in the 'finally' block to release resources
        secure_conn.close()
        print(f"[CLOSED] Connection with {addr} has been safely closed.")

def start_server():
    """
    Initializes the TCP socket, wraps it in a TLS layer, and starts listening.
    This is the main entry point for the server's lifecycle.
    """
    
    # 1. Pre-flight Check: Ensure security credentials exist
    if not os.path.exists(CERT_FILE) or not os.path.exists(KEY_FILE):
        print("[FATAL ERROR] SSL certificates missing. Run the OpenSSL command in the README.")
        sys.exit(1)

    # 2. Ensure log store file exists (create it if missing)
    if not os.path.exists(LOG_STORE):
        open(LOG_STORE, 'w').close()

    # 3. Create a basic TCP/IP socket (IPv4)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Allow the server to restart immediately on the same port without OS wait-time
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        # Bind the socket to the host and port
        server_socket.bind((HOST, PORT))
        # Listen for connections, allowing a 'backlog' of 10 waiting clients
        server_socket.listen(10) 
    except Exception as e:
        print(f"[BIND ERROR] Failed to bind to {HOST}:{PORT} - {e}")
        sys.exit(1)

    # 4. Setup SSL/TLS Context for modern, secure communication
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)

    print(f"[STARTING] Central Collector listening securely on port {PORT}...")

    try:
        while True:
            # Accept the raw incoming TCP connection
            client_socket, addr = server_socket.accept()
            
            try:
                # 5. The TLS Handshake: Upgrade the raw socket to an encrypted SSL socket
                secure_conn = context.wrap_socket(client_socket, server_side=True)
                
                # 6. Concurrency: Spawn a new worker thread so the main thread stays free
                # to accept the next incoming connection immediately.
                thread = threading.Thread(target=handle_client, args=(secure_conn, addr))
                thread.daemon = True # Thread terminates when the main program stops
                thread.start()
                
                # Report active client count (subtracting 1 for the main thread)
                print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
            except ssl.SSLError as e:
                print(f"[SSL REJECTED] Failed to establish secure connection with {addr} - {e}")
                client_socket.close()
                
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("\n[SHUTDOWN] Server shutting down gracefully via Keyboard Interrupt.")
    finally:
        # Ensure the main server socket is closed on exit
        server_socket.close()

if __name__ == "__main__":
    start_server()