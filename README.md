# Distributed Log Aggregation System

## Abstract
This project implements a secure, concurrent Distributed Log Aggregation System. It collects, centralizes, and manages log data generated from multiple distributed edge machines. 

## Mandatory Requirements Fulfilled
* **Low-Level Sockets**: Implemented using Python's native `socket` library. 
* **Secure Communication**: All control and data exchanges are encrypted using `ssl` wrapped sockets (TLS).
* **Concurrency**: The server supports multiple simultaneous clients using the `threading` module.

## Setup
1. Generate certificates: `mkdir certs` then `openssl req -x509 -newkey rsa:4096 -keyout certs/key.pem -out certs/cert.pem -days 365 -nodes`
2. Start server: `python3 server.py`
3. Start clients in new terminals: `python3 client.py 127.0.0.1 Machine_A`