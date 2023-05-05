from datetime import datetime
import socket,struct, threading, json, random, time
from TYPES import *
from netifaces import ifaddresses, AF_INET6

mcast_addr = 'ff05::4'
port = 3000
# Create a socket
sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)

NODE_NAME = socket.gethostname()

type_node, weigth, heigth, length, width = None

addresses = [i['addr'] for i in ifaddresses("eth0").setdefault(AF_INET6, [{'addr':'No IP addr'}])]
IPV6_ADDR = addresses[0]
cars_connected = {} #dicionario para saber quais os carros conectados

messages = [] #lista para guardar mensagens para depois reencaminhar

#pegar na localizacao do RSU
f_rsu = open("../n11.xy", "r")
pos_rsu = f_rsu.read().split()
pos_rsu_x = float(pos_rsu[0])
pos_rsu_y = float(pos_rsu[1])

#abrir o seu ficheiro de posicao
pos_x = 0 
pos_y = 0

def initCar(): #inicializar caracteristicas do carro
    type_node = random.randint(2,5)
    if type_node == CAR:
        weigth = 1000
        heigth = 1.5
        length = 4.0
        width = 1.7

    elif type_node == TRUCK:
        weigth = 10000
        heigth = 4.0
        length = 10.0
        width = 2.5

    elif type_node == MOTORCYCLE:
        weigth = 250
        heigth = 1.0
        length = 1.8
        width = 0.5
    elif type_node == BUS:
        weigth = 1200
        heigth = 4.0
        length = 12.0
        width = 2.5
        


def get_node_location():
    f_pos = open("../"+NODE_NAME+".xy", "r")
    pos = f_pos.read().split() 
    f_pos.close()
    pos_y = float(pos[0])
    pos_y = float(pos[1])
    return pos_x, pos_y


#envia uma mensagem com a sua posicao em multicast para os vizinhos
#assim, os vizinhos sabem a sua posicao e tambem sabem que estao conectados
def send_connection():
    while True:
        #ler a sua posicao regularmente
        x, y = get_node_location()        
        data = {
            FIELD_TYPE_NODE: type_node,	
            FIELD_NAME: NODE_NAME,
            FIELD_TYPE_MSG: CONNECTION_MSG,
            FIELD_POS_X: x, #!!! ler do ficheiro de posições
            FIELD_POS_Y: y,
            # Obter timestamp atual
            FIELD_TIMESTAMP:  datetime.timestamp(datetime.now())
        }
        data = json.dumps(data)
        # Envia a mensagem para o grupo multicast
        sock.sendto(data.encode(), (mcast_addr, port))
        #print("Send Connection: "+data)
        time.sleep(0.5)

def analyze_connections(): #atualizar as conexoes
    while True:
        for ip_node in list(cars_connected.keys()).copy():
            car = cars_connected.get(ip_node)        
            if datetime.timestamp(datetime.now()) - car.get(FIELD_TIMESTAMP) > 0.7:
                del cars_connected[ip_node]
        time.sleep(0.2)

#calular no com menor distancia do RSU
def calculate_dist():
    dist = ((pos_rsu_x-pos_x)**2+(pos_rsu_y-pos_y)**2)**(1/2) #calcualr a distancia do proprio no
    ipCarAux = IPV6_ADDR
    #variavel auxiliar para guardar a distancia min atual
    #ipCarAux = "" #variavel auxiliar para guardar o ip do carro com a dist min atual
    for ip_node in cars_connected.keys():
            car = cars_connected.get(ip_node)
            distAux = ((pos_rsu_x-car.get(FIELD_POS_X))**2+(pos_rsu_y-car.get(FIELD_POS_Y))**2)**(1/2)
            if distAux <= dist:
                ipCarAux = car.get(FIELD_IP)
                dist = distAux
    
    return ipCarAux


def send_msg(): #envia uma mensagem de 1 em 1 segundo com os seus dados    
    while True:
        next_hop = calculate_dist() #ver qual o vizinho mais proximo do RSU
        if next_hop is not None:
            data = {
                FIELD_TYPE_MSG: DATA_MSG,
                FIELD_ORIGIN: IPV6_ADDR,
                FIELD_NEXT_HOP: next_hop, #colocar o ip do next hop que vai encaminhar a mensagem
                #caracteristicas do no
                FIELD_NAME: NODE_NAME,
                FIELD_TYPE_NODE: type_node,
                FIELD_WEIGTH: weigth,
                FIELD_HEIGTH: heigth,
                FIELD_LENGTH: length,
                FIELD_WIDTH: width,
                #sensores
                FIELD_VELOCITY: random.randint(0,100),
                FIELD_RAIN: random.randint(0,1),
                FIELD_FOG: random.randint(0,1),
                FIELD_WET_FLOOR: random.randint(0,1),
                
                FIELD_TIMESTAMP: datetime.timestamp(datetime.now()),
                FIELD_DEST: RSU,
                FIELD_DEST_X: pos_rsu_x,
                FIELD_DEST_Y: pos_rsu_y
            }
            data = json.dumps(data)
            # Envia a mensagem para o grupo multicast
            sock.sendto(data.encode(), (mcast_addr, port))
        time.sleep(1)

""" a medida que recebe mensagens para encaminhar, adiciona-as numa lista
elas sao enviadas na ordem FIFO, depois de enviada a mensagem e eliminada """

def forward_msg(): #encaminhar mensagens recebidas de outros nos
    while True:
        if len(messages) > 0:
            msg = messages[0]
            next_hop = calculate_dist()
            messages.remove(msg)
            msg[FIELD_NEXT_HOP] = next_hop

            msg = json.dumps(msg)
            sock.sendto(msg.encode(), (mcast_addr, port))
        time.sleep(0.5)
        
""" Um no e capaz de receber dois tipos de mensagens:
    - uma que confirma a conexao com outro no (especie de keep alive do OSPF)
      --> armazena as conexoes num dicionario. estas mensagens contem a posicao dos nos vizinhos
    - mensagens de dados para encaminhar
      --> caso as mensagens de dados recebidas contiverem no campo "next hop" o
        proprio no, este armazena a mensagem para depois reencaminhar, caso contrario, descarta """

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
            # Da lista de endereços obter a primeira posicacao referente ao IPv6
            ip_node = addr[0]

            #verificar se a mensagem que recebeu ja n esta desatualizada
            if data[FIELD_TIMESTAMP] - datetime.timestamp(datetime.now()) < 0.7: 
                # Atualizar/inserir os campos de ultima conexão e de IP
                data[FIELD_IP] = ip_node
                
                # Inserir dados no dicionário
                update_cars_connected(ip_node, data)
              
        elif data[FIELD_TYPE_MSG] == DATA_MSG and data[FIELD_NEXT_HOP] == IPV6_ADDR:
                messages.append(data)
                show_recv = "["+str(addr[0])+"] "+ data.get(FIELD_NAME)+": "+ str(data.get(FIELD_VELOCITY))+" kmh"
                print(show_recv)

def update_cars_connected(ip_node, data):
    #if ip_node in cars_connected.keys():
    #    cars_connected[ip_node] = cars_connected[ip_node].update(data)
    #    return
    cars_connected[ip_node] = data

receive = threading.Thread(target=receive_msg, name="Recived Thread")
send = threading.Thread(target=send_msg, name="Send Thread")
send_conn = threading.Thread(target=send_connection, name="Send Conn Thread") #enviar mensagens de conexão em multicast
analyze = threading.Thread(target=analyze_connections, name="Analyze Thread")
forward = threading.Thread(target=forward_msg, name="Forward Thread")

if __name__ == "__main__":
    initCar()
    receive.start()
    send.start()
    send_conn.start()
    analyze.start()
    forward.start()

    # Aguarda até que ambas as threads terminem
    receive.join()
    send.join()
    send_conn.join()
    analyze.join()
    forward.join()