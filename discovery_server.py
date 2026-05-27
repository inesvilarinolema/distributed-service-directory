from time import sleep 
import zmq
import random 
import json
import time

context = zmq.Context()

#User ROUTER because we need to talk to multiple clients/services asynchronously
socket = context.socket(zmq.ROUTER)
socket.bind(f"tcp://localhost:{5555}")

poller = zmq.Poller()
poller.register(socket, zmq.POLLIN)

#Structure: {"ServiceType": {"IP:Port": {"expires_at": timestamp}}}
registry={}

print("[Discovery Server] Listening on port 5555..")

while True:
    events = dict(poller.poll(1000))

    #If a message has arrived
    if socket in events: 
        message = socket.recv_multipart()
        identity = message[0]
        payload = message[1]

        try:
            datos = json.loads(payload.decode('utf-8'))
        except json.JSONDecodeError:
            print("[Discovery Server] Ignored message: Invalid JSON format")
            continue

        #Registration logic
        if datos.get("action") == "register":
            service_type = datos.get("service_type")
            address = datos.get("address")
            #The registration lasts for 60s
            tiempo_expiracion = time.time() + 60 
            
            if service_type not in registry:
                registry[service_type] = {} #create its sub-dictionary
                
            registry[service_type][address] = {"expires_at": tiempo_expiracion}
            
            print(f"\n[REGISTER] {service_type} -> {address}")
            print(f"[Discovery Server] Current registry: {registry}")

            #Reply the service (ACK) so it knows it has been registered
            msg_exito = {"status": "success", "message": "Registration completed successfully"}
            response = json.dumps(msg_exito).encode('utf-8')
            socket.send_multipart([identity, response])

        #Discovery logic
        elif datos.get("action") == "discover":
            service_type = datos.get("service_type")

            #It they ask for a service that doesn't exist, return error
            if service_type not in registry:
                msg_error = {"status": "error", "message": "Service not found"}
                response = json.dumps(msg_error).encode('utf-8')
                socket.send_multipart([identity, response])
            else:
                #Load balancing: get all ips for the service
                avaliable_ips = list(registry[service_type].keys())
                selected_ip = random.choice(avaliable_ips) #pick one ip randomly

                #Send the selected IP to client
                msg_exito = {"status": "success", "address": selected_ip}
                enviar = json.dumps(msg_exito).encode('utf-8')
                socket.send_multipart([identity, enviar])

    #Cleanup
    #Ensured that inactive services are deleted eve if nobody sends messages
    time_now = time.time()
    items_delete = []

    #Look for services whose expiration date has passed
    for service_type, ips_dict in registry.items():
        for ip, datos_ip in ips_dict.items():
            if time_now > datos_ip["expires_at"]:
                items_delete.append((service_type, ip))

    #Delete the inactive services using temporary list
    for tipo_serv, ip_borrar in items_delete:
        del registry[tipo_serv][ip_borrar]
        print(f"[EVICTION] Expired and removed: {tipo_serv} -> {ip_borrar}")

        #Remove the service category entirely if it hasn't available IPS
        if not registry[tipo_serv]:
            del registry[tipo_serv]


    