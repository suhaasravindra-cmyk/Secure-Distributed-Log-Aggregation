# 🛡️ Secure Distributed Log Aggregation System
**A Multi-threaded, TLS-Encrypted Telemetry Framework**

---

## 📖 Project Overview
This project is a high-performance **Distributed Logging System** designed to collect system telemetry from multiple remote "edge" machines into a centralized, secure repository. It is engineered to solve the "Log Integrity" problem in distributed networks by utilizing **TLS 1.3** for end-to-end encryption and **JSON Serialization** for structured data interchange.

---

## 🏗️ System Architecture & Data Flow

The system architecture is divided into three distinct professional layers:

### 1. The Producer Layer (Distributed Agents)
Each client acts as a standalone monitoring agent capable of reporting its internal state to the master server.
* **Serialization:** Converts raw system events into a **JSON Schema** to ensure the server can parse metadata like source IDs and log levels without string-slicing errors.
* **Metadata Attachment:** Every log packet is injected with a high-precision UTC timestamp and a unique `machine_id` for traceability.

### 2. The Security Layer (TLS 1.3 Handshake)
Security is implemented at the **Presentation Layer** of the OSI model:
* **Asymmetric Encryption:** Uses **RSA-4096** bit keys for the initial identity verification between client and server.
* **Socket Wrapping:** The standard TCP socket is "wrapped" in an SSL context, ensuring that raw data never touches the network without encryption.

### 3. The Collector Layer (Centralized Multi-threaded Server)
The server is designed for high-concurrency environments:
* **Thread-per-Connection:** For every new client that connects, the server spawns a dedicated worker thread. This ensures that a slow connection from "Machine A" never delays a log from "Machine B."
* **Decryption & Aggregation:** The server uses its private key to decrypt the incoming stream, validates the JSON structure, and appends it to `centralized_logs.txt`.



---

## 🛠️ Technical Specifications

| Component | Technology | Technical Justification |
| :--- | :--- | :--- |
| **Language** | Python 3.12+ | Rapid prototyping with robust standard libraries for SSL and Threading. |
| **Security** | TLS 1.3 | Modern standard; prevents POODLE and BEAST attacks found in older SSL versions. |
| **Format** | JSON | Standardized data format; allows for future integration with ELK stack or Splunk. |
| **Protocol** | TCP/IP | Ensures "Connection-Oriented" reliability; no log packets are lost or out-of-order. |
| **Concurrency** | `threading` | Allows the server to remain responsive while performing heavy I/O operations. |

---

## 🔒 Security Analysis & Engineering Proof

### 🔐 The TLS Handshake Process
When a client connects, the following "Handshake" occurs before any log data is sent:
1. **Client Hello:** Client proposes encryption algorithms.
2. **Server Certificate:** Server sends `cert.pem` to prove its identity.
3. **Key Exchange:** Both parties generate a temporary "Session Key."
4. **Encrypted Channel:** All JSON logs are now encrypted using the Session Key (Symmetric Encryption for speed).



### ✅ Data Integrity & Confidentiality
* **Confidentiality:** If a packet capture tool (like Wireshark) is used, the payload appears as random ciphertext.
* **Integrity Protection:** Every packet includes a Message Authentication Code (MAC). If any data is tampered with by a third party during transit, the TLS layer will drop the connection immediately.

---

## 📝 Step-by-Step Execution Guide

### Step 1: Security Setup (RSA Certificate Generation)
The system requires a Self-Signed Certificate to establish the secure tunnel. Run this command in your terminal:
```bash
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

### Step 2: Launch the Central Collector
The server must be started first to initialize the network listener and the SSL context. This central node handles the decryption and aggregation of all incoming data.

Run the following command in your primary terminal:
```bash
python server.py

### Step 3: Deploy Distributed Agents (Concurrent Simulation)
To demonstrate the server's **Multi-threading** and **Concurrency** capabilities, open multiple terminal windows to simulate different machines connecting to the central collector simultaneously.

**Terminal A (Simulating Machine 1):**
```bash
python client.py 127.0.0.1 Machine_A
python client.py 127.0.0.1 Machine_B

---

## 🔒 Security & Performance Analysis

### 🔐 The TLS 1.3 Advantage
By using **TLS 1.3**, the project ensures that:
* **Confidentiality:** Every log packet is encrypted with **AES-256-GCM**. Even if an attacker "sniffs" the network traffic, the data remains indecipherable ciphertext.
* **Perfect Forward Secrecy:** If a long-term key is compromised in the future, past session data remains secure.
* **Data Integrity:** The system uses Message Authentication Codes (MAC) to ensure that logs are not tampered with during transit.

### 🧵 Multi-threaded Scalability
The server utilizes a **Thread-per-Connection** model. This allows for:
* **Non-blocking I/O:** Multiple clients can stream logs simultaneously without waiting for others to finish.
* **Fault Isolation:** A crash or slow connection in one client thread does not affect the performance of other active monitoring agents.

---