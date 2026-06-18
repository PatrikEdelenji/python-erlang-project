Network Intelligence Simulator

This is a small Erlang/OTP + Python project that simulates telecom network nodes and monitors their metrics.

The Erlang part simulates multiple network nodes as supervised worker processes. Each node sends metrics such as latency, packet loss, CPU usage, and memory usage to a Python FastAPI backend, and the backend stores the metrics in PostgreSQL and creates alerts when values exceed defined thresholds.

How to run
Prerequisites

Make sure the following are installed:

Python
Erlang/OTP
Docker Desktop

1. Start the backend

From the project root:

start_backend.bat

This starts PostgreSQL using Docker Compose and runs the FastAPI backend.

The API documentation is available at:

http://127.0.0.1:8000/docs

2. Start the Erlang simulator

Open a second terminal from the project root:

start_simulator.bat

This compiles and starts the Erlang/OTP simulator.

3. Stop the application

Stop the backend or simulator with:

Ctrl + C

Stop PostgreSQL with:

docker compose down

Node configuration

Simulated nodes are configured in:

simulator/nodes.config

Example:

[
{"erlang_node_001", stable, 0},
{"erlang_node_002", unstable, 3},
{"erlang_node_003", critical, 10},
{"erlang_node_004", unstable, 5}
].

Each entry contains:

node_id, risk_profile, crash_chance_percent
API endpoints

After starting the backend, open:

http://127.0.0.1:8000/docs

Available endpoints:

GET /health
POST /metrics
GET /metrics
GET /metrics/{node_id}
GET /alerts
GET /nodes
How it works

The Erlang simulator starts several supervised node workers. Each worker periodically generates random network metrics and sends them to the FastAPI backend using HTTP POST requests.

The Python backend validates incoming metrics, stores them in PostgreSQL, and creates alerts for problematic values such as:

high latency
packet loss
high CPU usage
high memory usage

If a simulated Erlang node crashes, the OTP supervisor restarts it automatically.
