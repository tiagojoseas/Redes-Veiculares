import datetime
import socket,struct, threading, json, random, time
from TYPES import *

mcast_addr = 'ff05::4'
port = 3000
# Create a socket
sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)

NODE_NAME = socket.gethostname()
IPV6_ADDR = socket.gethostbyname(NODE_NAME)

cars_connected = {} #dicionario para saber quais os carros conectados

messages = [] #lista para guardar mensagens para depois reencaminhar

#envia uma mensagem com a sua posicao em multicast para os vizinhos
#assim, os vizinhos sabem a sua posicao e tambem sabem que estao conectados
def send_connection():
    while True:
        data = {
            FIELD_TYPE_MSG: CONNECTION_MSG,
            FIELD_POS_X: 5.0, #!!! ler do ficheiro de posições
            FIELD_POS_Y: 6.0
        }
        data = json.dumps(data)
        # Envia a mensagem para o grupo multicast
        sock.sendto(data.encode(), (mcast_addr, port))
        time.sleep(0.5)

def analyze_connections(): #atualizar as conexões
    while True:

        for ip_node in cars_connected.keys():
            car = cars_connected.get(ip_node)
        
            if datetime.timestamp(datetime.now()) - car.get(FIELD_LAST_CONNECTION) > 1.1:
                del cars_connected[ip_node]

def send_msg(): 
    
    while True:
        # Lê a mensagem a ser enviada do usuário
        #message = input( )
        data = {
            FIELD_TYPE_MSG: DATA_MSG,
            FIELD_OR: IPV6_ADDR,
            FIELD_NEXT_HOP: "ipv6_addr", #colocar o ip do next hop qe vai encaminhar a mensagem
	        FIELD_TYPE_NODE: CAR,	
            FIELD_NAME: NODE_NAME,
            FIELD_VELOCITY: random.randint(0,100),
            FIELD_DEST: RSU
        }
        data = json.dumps(data)
        # Envia a mensagem para o grupo multicast
        sock.sendto(data.encode(), (mcast_addr, port))
        time.sleep(1)

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
        data = json.loads(data.decode()) #converter para json

        if data[FIELD_TYPE_MSG] == CONNECTION_MSG:
            # Obter timestamp atual
            time_rc = datetime.timestamp(datetime.now())
            # Converter dados para JSON
            data = json.loads(data.decode())
            # Da lista de endereços obter a primeira posicacao referente ao IPv6
            ip_node = addr[0]

            # Atualizar/inserir os campos de ultima conexão e de IP
            data[FIELD_IP] = ip_node
            data[FIELD_LAST_CONNECTION] = time_rc

            # Inserir dados no dicionário
            cars_connected[ip_node] = data
        
        elif data[FIELD_TYPE_MSG] == DATA_MSG:
            if data[FIELD_NEXT_HOP] == IPV6_ADDR:
                messages.append(data)


        #print("From " + str(addr) + ": " + data.decode())
        show_recv = "["+str(addr[0])+"] "+ data.get(FIELD_NAME)+": "+ str(data.get(FIELD_VELOCITY))+" kmh"
        print(show_recv)

receive = threading.Thread(target=receive_msg)
send = threading.Thread(target=send_msg)
send_conn = threading.Thread(target=send_connection) #enviar mensagens de conexão em multicast
analyze = threading.Thread(target=analyze_connections)

receive.start()
send.start()
send_conn.start()
analyze.start()

# Aguarda até que ambas as threads terminem
receive.join()
send.join()
send_conn.join()
analyze.join()