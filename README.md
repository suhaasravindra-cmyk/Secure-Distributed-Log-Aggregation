# 🚀 Distributed Log Aggregation & Analysis System

A lightweight, real-time telemetry framework designed to aggregate logs from distributed machines into a centralized repository for visual analysis. This system uses **UDP sockets** for log transmission and **Pandas/Matplotlib** for data insights.

---

## 🛠️ Features
* **Real-time Log Streaming:** Uses UDP protocol for fast, non-blocking log transmission.
* **Centralized Storage:** Automatically captures and stores incoming telemetry into a structured `logs.csv`.
* **Data Visualization:** Generates distribution charts (Bar/Pie) and throughput trends (Time-series) to monitor system health.
* **Automated Setup:** Server script automatically initializes the CSV database with headers if it doesn't exist.

---

## 📂 Project Structure
* `server.py`: The central aggregator that listens for incoming UDP packets and writes to the CSV.
* `client.py`: The edge-node simulator that generates and sends logs (INFO, WARNING, ERROR).
* `analyzer.py`: The data science component that processes the CSV and generates visual reports.
* `logs.csv`: The persistent data store for all aggregated telemetry.

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have Python installed, along with the required data analysis libraries:
```bash
pip install pandas matplotlib
### 2. Launch Sequence

To run the full pipeline, open **three separate terminal windows** and execute the scripts in the following order. This ensures the receiver is ready before the data starts flowing.

| Order | Component | Command | Purpose |
| :--- | :--- | :--- | :--- |
| **1** | **Server** | `python server.py` | Starts the listener, opens port `9999`, and initializes `logs.csv`. |
| **2** | **Client** | `python client.py` | Begins generating and streaming simulated log data every second. |
| **3** | **Analyzer** | `python analyzer.py` | Reads the collected data and generates the visual dashboard. |

---

**💡 Pro-Tip:** Keep the **Server** and **Client** running in the background. You can run the **Analyzer** script multiple times to see the graphs update as more data is collected!
### 3. Execution Tips
Order Matters: Always start the Server first. UDP is "fire and forget," so if the client sends data while the server is offline, those logs will be lost.

Data Collection: Let the Client run for at least 15–20 seconds before running the Analyzer. This ensures there is enough data in logs.csv to create meaningful graphs.

Live Updates: You can leave the Server and Client running and simply re-run python analyzer.py whenever you want to see the updated charts.

Stopping: To stop the data stream or the server, click into their respective terminals and press Ctrl + C.
