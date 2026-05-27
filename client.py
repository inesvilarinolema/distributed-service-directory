from time import sleep 
import zmq
import json
import sys

if len(sys.argv) != 2:
    print("Error -> Usage: python client.py <service_type>")
    print("Example: python service.py ImageProcessor")
    sys.exit(1)

service_argument = sys.argv[1]

context = zmq.Context()

#Connect to the central server to ask for the directory
socket = context.socket(zmq.DEALER)
socket.connect(f"tcp://localhost:{5555}")

discovery_message = {
    "action": "discover",
    "service_type": service_argument
}

print(f"[Client] Asking Discovery Server for a '{service_argument}' worker...")

payload = json.dumps(discovery_message).encode('utf-8')
socket.send(payload)

respuesta = socket.recv()
datos = json.loads(respuesta.decode('utf-8'))

if datos.get("status") == "error":
    print(f"[Client] Server replied: {datos.get('message')}")
    sys.exit(1)

#Extract the IP that the server's load balancer has chosen
address = datos.get("address")
print(f"[Client] Found '{service_argument}' at {address}. Connecting directly...")

#User request socket to connect to the worker REP socket
socket_request = context.socket(zmq.REQ)
socket_request.connect(f"tcp://{address}")

print(f"[Client] Sending workload...")

#Send the workload to the service
socket_request.send_string(f"Hello, I need you to work as {service_argument}. Process this!")

#Block and wait until the service finishes 
answer = socket_request.recv_string()
print(f"[Client] The service answered: {answer}")