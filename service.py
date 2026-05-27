from time import sleep 
import time
import zmq
import json
import threading
import sys

if len(sys.argv) != 3:
    print("Error -> Usage: python service.py <service_type> <port>")
    print("Example: python service.py ImageProcessor 8080")
    sys.exit(1)


type_service_argument = sys.argv[1]
port_argument = sys.argv[2]

context = zmq.Context()

#Message template
mensaje_registro = {
    "action": "register",
    "service_type": type_service_argument,
    "address": f"127.0.0.1:{port_argument}"
}

address = f"127.0.0.1:{port_argument}"

#Secondary thread, to registry maintenance
def keep_register() -> None:

    #Use DEALER because we are an asynchronous client talking to the server's ROUTER
    socket = context.socket(zmq.DEALER)
    socket.connect(f"tcp://localhost:{5555}")

    while True:
        payload = json.dumps(mensaje_registro).encode('utf-8')
        socket.send(payload)
        #print(f"[{tyspe_service_argument}] Heartbeat registration sent.")

        #Wait for the ACK
        datos_server = socket.recv()
        print(f"[{type_service_argument}] Server replied: {datos_server}")        
        
        time.sleep(45)

thread_heating = threading.Thread(target=keep_register, daemon=True)
thread_heating.start()

#Use reply pattern to handle direct request from clients
socket_conection = context.socket(zmq.REP)
socket_conection.bind(f"tcp://{address}")

print(f"[{type_service_argument}] Service is up and listening on port {port_argument}...")

while True:
    #Wait for a client to connect and ask
    request = socket_conection.recv_string()
    print(f"[{type_service_argument}] Received request: {request}")

    time.sleep(2)
    
    answer = f"Task successfully processed by {type_service_argument}!"
    socket_conection.send_string(answer)
 