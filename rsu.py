import socket,struct, threading, json
from datetime import datetime
from TYPES import *

mcast_addr = 'ff05::4'
port = 3000
# Create a socket
sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)

cars_connected = {}
last_status = {}

def send_msg():
    
    while True:
        # Lê a mensagem a ser enviada do usuário
        input("Prima enter para mostrar os dados\n")
        print("-"*50)
        cars_connected_cp = cars_connected.copy()
        for ip_node in cars_connected_cp.keys():
            car = cars_connected_cp.get(ip_node)
            status = car.get(FIELD_STATUS_CONNECTION)
            show_recv = "["+str(ip_node)+"] " 
            show_recv += car.get(FIELD_NAME)+" - "+ str(car.get(FIELD_VELOCITY))+" kmh"
            show_recv += "("+str(car.get(FIELD_LAST_CONNECTION))+") -> "
            show_recv += "DISCONNECTED" if status==0 else "CONNECTED"
            
            print(show_recv)
        print("-"*50)
        # Envia a mensagem para o grupo multicast
        #sock.sendto(message.encode(), (mcast_addr, port))


def analyze_connections():
    while True:
        # Lê a mensagem a ser enviada do usuário
        cars_connected_cp = cars_connected.copy()

        for ip_node in cars_connected_cp.keys():
            car = cars_connected_cp.get(ip_node)
            if ip_node not in last_status.keys():
                show_recv = "["+str(ip_node)+"] "+ car.get(FIELD_NAME)+": NEW CAR" 
                print(show_recv)
                last_status[ip_node] = None

            else:
                status = STATUS_CONNECTED
                if datetime.timestamp(datetime.now()) - car.get(FIELD_LAST_CONNECTION) > 1.2:
                    status = STATUS_DISCONNECTED

                if last_status.get(ip_node) != status:  
                    show_recv = "["+str(ip_node)+"] "+ car.get(FIELD_NAME)+" -> "+("DISCONNECTED" if status == 0 else "CONNECTED")
                    last_status[ip_node] = status
                    cars_connected[ip_node][FIELD_STATUS_CONNECTION]=status
                    print(show_recv) 

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
        # Obter dado e endereco
        data, addr = sock.recvfrom(1024)
        # Obter timestamp atual
        time_rc = datetime.timestamp(datetime.now())
        # Converter dados para JSON
        data = json.loads(data.decode())
        # Da lista de endereços obter a primeira posicacao referente ao IPv6
        ip_node = addr[0]

        # Atualizar/inserir os campos de ultima conexão e de IP
        data[FIELD_IP] = ip_node
        data[FIELD_LAST_CONNECTION] = time_rc
        data[FIELD_STATUS_CONNECTION] = STATUS_CONNECTED

        # Inserir dados no dicionário
        cars_connected[ip_node] = data
       
if __name__ == "__main__":
    send = threading.Thread(target=send_msg)
    analyze = threading.Thread(target=analyze_connections)
    receive = threading.Thread(target=receive_msg)

    send.start()
    analyze.start()
    receive.start()

    # Aguarda até que ambas as threads terminem
    send.join()
    analyze.join()
    receive.join()
