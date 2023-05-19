import socket,struct, threading, json
from datetime import datetime
from TYPES import *

mcast_addr = 'ff05::4'
port = 3000

# Create a sockets
# Bind the socket to an address and port
sock_cars = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
sock_cars.bind(('::', port))

# Bind the socket to a local address and port
sock_server = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
local_address = "2001:690:2280:820::2"  # Use any available IPv6 address on the local machine
server_address = "2001:690:2280:820::3" 
server_rsu_port = 9999 
sock_server.bind((local_address, server_rsu_port))

cars_neigh_connected = {}
last_status = {}
jamn_data = {}

def print_data():    
    while True:
        # Lê a mensagem a ser enviada do usuário
        input("Prima enter para mostrar os dados\n")
        print("-"*50)
        cars_neigh_connected_cp = cars_neigh_connected.copy()
        for ip_node in cars_neigh_connected_cp.keys():
            car = cars_neigh_connected_cp.get(ip_node)
            status = car.get(FIELD_STATUS_CONNECTION)
            show_recv = "["+str(ip_node)+"] " 
            show_recv += car.get(FIELD_NAME)+" - "#+ str(car.get(FIELD_VELOCITY))+" kmh"
            show_recv += "("+str(car.get(FIELD_LAST_CONNECTION))+") -> "
            show_recv += "DISCONNECTED" if status==0 else "CONNECTED"
            
            print(show_recv)
        print("-"*50)
        # Envia a mensagem para o grupo multicast

def analyze_connections():
    while True:
        # Lê a mensagem a ser enviada do usuário
        cars_neigh_connected_cp = cars_neigh_connected.copy()

        for ip_node in cars_neigh_connected_cp.keys():
            car = cars_neigh_connected_cp.get(ip_node)
            if ip_node not in last_status.keys():
                show_recv = "["+str(ip_node)+"] "+ car.get(FIELD_NAME)+": NEW CAR" 
                print(show_recv, car[FIELD_POS_X], car[FIELD_POS_Y])
                last_status[ip_node] = None
            else:
                status = STATUS_CONNECTED
                if datetime.timestamp(datetime.now()) - car.get(FIELD_LAST_CONNECTION) > 1:
                    status = STATUS_DISCONNECTED
                if last_status.get(ip_node) != status:  
                    show_recv = "["+str(ip_node)+"] "+ car.get(FIELD_NAME)+" -> "+("DISCONNECTED" if status == 0 else "CONNECTED")
                    last_status[ip_node] = status
                    cars_neigh_connected[ip_node][FIELD_STATUS_CONNECTION]=status
                    print(show_recv) 

        # Envia a mensagem para o grupo multicast
        #sock_cars.sendto(message.encode(), (mcast_addr, port))

#calular nó com menor distancia da area
def get_next_node(node_x, node_y):
    ipCarAux = list(cars_neigh_connected.keys())[0]
    dist = ((node_x-cars_neigh_connected[ipCarAux][FIELD_POS_X])**2+(node_y-cars_neigh_connected[ipCarAux][FIELD_POS_Y])**2)**(1/2) #buscar o primeiro nó da lista e calcular a dist
    for ip_node in cars_neigh_connected.keys():
            car = cars_neigh_connected[ip_node]
            distAux = ((node_x-car.get(FIELD_POS_X))**2+(node_y-car.get(FIELD_POS_Y))**2)**(1/2)
            if distAux <  dist:
                ipCarAux = car[FIELD_IP]
                dist = distAux
    
    return ipCarAux

def receive_msg_from_cars():
    
    # Set the multicast group address and interface index
    iface_index = 0

    # Construct the group address tuple
    mcast_group = socket.inet_pton(socket.AF_INET6, mcast_addr)
    mcast_if = struct.pack('@I', iface_index)
    mcast_group_tuple = mcast_group + mcast_if

    # Join the multicast group
    sock_cars.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_JOIN_GROUP, mcast_group_tuple)
  
    while True:
        # Obter dado e endereco
        data, addr = sock_cars.recvfrom(1024)
        # Obter timestamp atual
        time_rc = datetime.timestamp(datetime.now())
        # Converter dados para JSON
        data = json.loads(data.decode())
        # Da lista de endereços obter a primeira posicao referente ao IPv6
        ip_node = addr[0]

        # Atualizar/inserir os campos de ultima conexão e de IP
        data[FIELD_IP] = ip_node
        data[FIELD_LAST_CONNECTION] = time_rc
        data[FIELD_STATUS_CONNECTION] = STATUS_CONNECTED


        # Inserir dados no dicionário
        if data[FIELD_TYPE_MSG]!= DENM_MSG:
            sock_server.sendto(json.dumps(data).encode(), (server_address, server_rsu_port))
        if data[FIELD_TYPE_MSG] == CONNECTION_MSG:
            update_cars_neigh_connected(data)
        if data[FIELD_TYPE_MSG] == CAM_MSG:
            print("RSU << CAM ",data[FIELD_NAME])

def receive_msg_from_server():
    while True:
        # Obter dado e endereco
        data, addr = sock_server.recvfrom(1024)
        data = json.loads(data)
        if data[FIELD_TYPE_MSG] == DENM_MSG:
            if data[DENM_TYPE] == TRAFFIC_JAM:
                next_hop_addr = get_next_node(data[FIELD_EPICENTER_X],data[FIELD_EPICENTER_Y])
                print("RSU << TRAFFIC_JAM at: ","x:"+data[FIELD_EPICENTER_X], "y:"+data[FIELD_EPICENTER_Y], "("+data[FIELD_EPICENTER_NAME]+") >>", cars_neigh_connected[next_hop_addr][FIELD_NAME])
                data[FIELD_NEXT_HOP] = next_hop_addr 
                sock_cars.sendto(json.dumps(data).encode(), (mcast_addr, port))
                #linha para enviar para o carro (nao sei como)
               
def update_cars_neigh_connected(data):   
    cars_neigh_connected[data[FIELD_ORIGIN]] = data    

if __name__ == "__main__":
    print_th = threading.Thread(target=print_data, name="Send Thread")
    analyze = threading.Thread(target=analyze_connections, name="Analyze Thread")
    receive_from_cars = threading.Thread(target=receive_msg_from_cars, name="Recived Cars Thread")
    receive_from_server = threading.Thread(target=receive_msg_from_server, name="Recived Server Thread")

    print_th.start()
    analyze.start()
    receive_from_cars.start()
    receive_from_server.start()

    # Aguarda até que ambas as threads terminem
    print_th.join()
    analyze.join()
    receive_from_cars.join()
    receive_from_server.join()