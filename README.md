# ZeroMQ Fault-Tolerant Service Discovery Server

A robust, asynchronous, and fault-tolerant Service Discovery system built with Python and ZeroMQ. This project simulates a microservices architecture where worker nodes dynamically register themselves, and clients query a central directory to find available services.

## Features

* **Asynchronous Architecture:** Uses ZMQ `ROUTER` and `DEALER` patterns at the directory level to prevent blocking.
* **Fault Tolerance (Eviction):** The server utilizes a `Poller` to actively monitor service health. Services that fail to send a heartbeat within 60 seconds are gracefully evicted from the registry without crashing the server.
* **Dynamic Heartbeats:** Worker nodes use a background daemon thread to periodically renew their registration (every 45 seconds) while their main thread handles actual workloads.
* **Load Balancing:** When multiple instances of the same service type are registered, the discovery server uses random sampling to distribute client requests evenly.
* **Direct P2P Processing:** Once a client discovers a service's IP and port, it connects directly to the worker using the `REQ/REP` pattern, completely bypassing the central server for the actual workload.

## Architecture & ZMQ Patterns

1.  **Discovery Server (`ROUTER`):** Listens asynchronously. Maps `service_type` to a list of available `IP:Port` addresses.
2.  **Worker Service (`DEALER` + `REP`):** * Uses a `DEALER` socket in a background thread to send heartbeats to the server.
    * Uses a `REP` socket in the main thread to process tasks from clients.
3.  **Client (`DEALER` + `REQ`):**
    * Uses a `DEALER` socket to ask the server for a service address.
    * Uses a `REQ` socket to connect directly to the provided worker address.

## Prerequisites

You will need Python 3.x and the `pyzmq` library. Install the dependency using pip:

```bash
pip install pyzmq

```

## How to Run the Demonstration

To observe the load balancing and fault tolerance in action, open 4 separate terminals and run the scripts in the following order:

### 1. Start the Discovery Server

Launch the central directory on Terminal 1:

```bash
python discovery_server.py

```

### 2. Start the Worker Services

Launch two instances of the same service on different ports to see the load balancer in action (Terminals 2 and 3):

```bash
python service.py ImageProcessor 8080
python service.py ImageProcessor 8081

```

*(You can also launch a different service type, e.g., `python service.py DataAnalyzer 9000`)*

### 3. Run the Client

On Terminal 4, ask for the service you just deployed. Run this command multiple times to see the server randomly assigning you to port `8080` or `8081`:

```bash
python client.py ImageProcessor

```

### 4. Test Fault Tolerance (Simulate a Crash)

To test the eviction logic, go to one of your worker terminals (e.g., Terminal 2) and force-kill the process using `Ctrl+C`.
Keep an eye on the Discovery Server terminal. After approximately 60 seconds of missed heartbeats, the server will log an `[EVICTION]` message and safely remove the dead node from the registry.

**Inés Vilariño Lema** *Project developed for the Distributed and Concurrent Programming course.*

