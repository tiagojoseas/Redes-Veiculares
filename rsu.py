import socket,struct, threading, json
from datetime import datetime

mcast_addr = 'ff05::4'
port = 3000
# Create a socket
sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)

cars_connected = {}

def send_msg():
    
    while True:
        # Lê a mensagem a ser enviada do usuário
        message = input( )
        for car in cars_connected:
            print(car)
        # Envia a mensagem para o grupo multicast
        #sock.sendto(message.encode(), (mcast_addr, port))

def receive_msg():
    # Bind the socket to an address and port
    sock.bind(('::', port))

    # Set the multicast group address and interface index

    iface_index = 0

    # Construct the group address tuple
    mcast_group = socket.inet_pton(socket.AF_INET6, mcast_addr)
    mcast_if = struct.pack('@I', iface_index)
    mcast_group_tuple = mcast_group + mcast_if

    # Join the multicast group
    sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_JOIN_GROUP, mcast_group_tuple)
  
    while True:
        data, addr = sock.recvfrom(1024)
        data = json.loads(data)
        data["last_connection"] = str(datetime.now())
        cars_connected[str(addr[0])] = data
        print(data)
        #print("[+]",data.get("car"),"-", data.get("velocity")+" kmh")
        #print(data[car], data[velocity])
        #print("From " + str(addr) + ": " + data.decode())

send = threading.Thread(target=send_msg)
receive = threading.Thread(target=receive_msg)

send.start()
receive.start()

# Aguarda até que ambas as threads terminem
send.join()
receive.join()
