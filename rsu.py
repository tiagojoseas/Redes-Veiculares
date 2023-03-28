import socket,struct, threading, json
from datetime import datetime
from TYPES import *
from prettytable import PrettyTable

mcast_addr = 'ff05::4'
port = 3000
# Create a socket
sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)

cars_connected = {}

table = PrettyTable(["IP", "NOME NÓ", "VELOCIDADE (kmh)", "ÚLTIMA CONEXÇÃO"])
def send_msg():
    
    while True:
        # Lê a mensagem a ser enviada do usuário
        input("\n\nPrima enter para mostrar os dados\n\n")

        print("Conectados "+str(len(cars_connected))+" carros\n")

        for ip_node in cars_connected.keys():
            car = cars_connected[ip_node]
            dt = datetime.fromtimestamp(car.get(FIELD_LAST_CONNECTION))
            table.addRow([ip_node,car.get(FIELD_NAME), car.get(FIELD_VELOCITY), dt])
            #show_recv = "["+str(ip_node)+"] "+ car.get(FIELD_NAME)+" - "+ str(car.get(FIELD_VELOCITY))+" kmh ("+str(dt)+")"
            #print(show_recv)
        print(table)
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

        # Inserir dados no dicionário
        cars_connected[ip_node] = data
       
if __name__ == "__main__":
    send = threading.Thread(target=send_msg)
    receive = threading.Thread(target=receive_msg)

    send.start()
    receive.start()

    # Aguarda até que ambas as threads terminem
    send.join()
    receive.join()
