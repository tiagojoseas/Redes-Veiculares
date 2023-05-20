from datetime import datetime
import socket,struct, threading, json, random, time
from TYPES import *
from netifaces import ifaddresses, AF_INET6

mcast_addr = 'ff05::4'
port = 3000
# Create a socket
sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)

NODE_NAME = socket.gethostname()

type_node = None
weigth=None
heigth=None
length=None
width=None
velocity = None

addresses = [i['addr'] for i in ifaddresses("eth0").setdefault(AF_INET6, [{'addr':'No IP addr'}])]
IPV6_ADDR = addresses[0]
cars_connected = {} #dicionario para saber quais os carros conectados

messages = [] #lista para guardar mensagens para depois reencaminhar
colision_buffer = [] #lista para guardar mensagens de colisao para depois reencaminhar
#pegar na localizacao do RSU
f_rsu = open("../n11.xy", "r")
pos_rsu = f_rsu.read().split(" ")
pos_rsu_x = float(pos_rsu[0])
pos_rsu_y = float(pos_rsu[1])

#abrir o seu ficheiro de posicao
pos_x = 0 
pos_y = 0

def initCar(): #inicializar caracteristicas do carro
    global weigth, heigth, length, width, velocity, type_node
    type_node = random.randint(CAR,BUS)
    if type_node == CAR:
        weigth = 1000
        heigth = 1.5
        length = 4.0
        width = 1.7
        velocity = random.randint(60,100)

    elif type_node == TRUCK:
        weigth = 10000
        heigth = 4.0
        length = 10.0
        width = 2.5
        velocity = random.randint(30,60)

    elif type_node == MOTORCYCLE:
        weigth = 250
        heigth = 1.0
        length = 1.8
        width = 0.5
        velocity = random.randint(30,100)

    elif type_node == BUS:
        weigth = 1200
        heigth = 4.0
        length = 12.0
        width = 2.5
        velocity = random.randint(20,50)

    print(NODE_NAME,"VELOCITY:",velocity)
        

#pegar na localizacao de um no
def get_node_location(name):
    f_pos = open("../"+name+".xy", "r")
    pos = f_pos.read().split(" ") 
    f_pos.close()
    pos_x = float(pos[0])
    pos_y = float(pos[1])
    return pos_x, pos_y


#envia uma mensagem com a sua posicao em multicast para os vizinhos
#assim, os vizinhos sabem a sua posicao e tambem sabem que estao conectados
def send_connection():
    while True:
        #ler a sua posicao regularmente
        x, y = get_node_location(NODE_NAME)  
        data = {
            FIELD_TYPE_NODE: type_node,	
            FIELD_ORIGIN: IPV6_ADDR,
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
        #print(NODE_NAME,"Send Connection: "+data)
        time.sleep(0.5)

def analyze_connections(): #atualizar as conexoes
    while True:
        for ip_node in list(cars_connected.keys()).copy():
            car = cars_connected.get(ip_node)        
            if datetime.timestamp(datetime.now()) - car.get(FIELD_TIMESTAMP) > 1.7:
                del cars_connected[ip_node]
        time.sleep(0.2)


#calular no com menor distancia do RSU
def get_next_node(node_x, node_y):
    dist = ((node_x-pos_x)**2+(node_y-pos_y)**2)**(1/2) #calcualr a distancia do proprio no
    ipCarAux = IPV6_ADDR
    #variavel auxiliar para guardar a distancia min atual
    #ipCarAux = "" #variavel auxiliar para guardar o ip do carro com a dist min atual
    for ip_node in cars_connected.keys():
            car = cars_connected[ip_node]
            distAux = ((node_x-car.get(FIELD_POS_X))**2+(node_y-car.get(FIELD_POS_Y))**2)**(1/2)
            if distAux <= dist:
                ipCarAux = car[FIELD_ORIGIN]
                dist = distAux
    
    return ipCarAux

def get_next_node_traffic_jam(node_x, node_y,radius_s, radius_b):
    
    dist = ((node_x-pos_x)**2+(node_y-pos_y)**2)**(1/2) #calcualr a distancia do proprio no
    ipCarAux = IPV6_ADDR
    #variavel auxiliar para guardar a distancia min atual
    #ipCarAux = "" #variavel auxiliar para guardar o ip do carro com a dist min atual
    for ip_node in cars_connected.keys():
            car = cars_connected[ip_node]
            distAux = ((node_x-car.get(FIELD_POS_X))**2+(node_y-car.get(FIELD_POS_Y))**2)**(1/2)
            if distAux > dist and distAux > radius_s and distAux < radius_b:
                ipCarAux = car[FIELD_ORIGIN]
                dist = distAux
            elif distAux <= dist and distAux > radius_b:
                ipCarAux = car[FIELD_ORIGIN]
                dist = distAux

    
    return ipCarAux


def send_CAM(): #envia uma mensagem de 1 em 1 segundo com os seus dados    
    while True:
        next_hop = get_next_node(pos_rsu_x, pos_rsu_y) #ver qual o vizinho mais proximo do RSU
        if next_hop is not None:
            x, y = get_node_location(NODE_NAME)  
            msg_cam = {
                FIELD_TYPE_MSG: CAM_MSG,
                FIELD_ORIGIN: IPV6_ADDR,
                FIELD_NEXT_HOP: next_hop, #colocar o ip do next hop que vai encaminhar a mensagem
                #caracteristicas do no
                FIELD_NAME: NODE_NAME,
                FIELD_TYPE_NODE: type_node,
                FIELD_WEIGTH: weigth,
                FIELD_HEIGTH: heigth,
                FIELD_LENGTH: length,
                FIELD_WIDTH: width,
                #posicao atual do nó
                FIELD_POS_X: x, 
                FIELD_POS_Y: y,
                #sensores
                FIELD_VELOCITY: velocity,
                FIELD_RAIN: random.randint(0,1),
                FIELD_FOG: random.randint(0,1),
                FIELD_WET_FLOOR: random.randint(0,1),
                
                FIELD_TIMESTAMP: datetime.timestamp(datetime.now()),
                FIELD_DEST: RSU,
                FIELD_DEST_X: pos_rsu_x,
                FIELD_DEST_Y: pos_rsu_y
            }
            msg_cam = json.dumps(msg_cam)
            # Envia a mensagem para o grupo multicast
            sock.sendto(msg_cam.encode(), (mcast_addr, port))
        time.sleep(1)

""" a medida que recebe mensagens para encaminhar, adiciona-as numa lista
elas sao enviadas na ordem FIFO, depois de enviada a mensagem e eliminada """

def forward_msg(): #encaminhar mensagens recebidas de outros nos
    while True:
        # verificar as DENM
        denm_arr=[]
        for msg in messages:
            if msg[FIELD_TYPE_MSG]== DENM_MSG:
                messages.remove(msg)
                if msg[DENM_TYPE]== TRAFFIC_JAM:
                    x, y = get_node_location(NODE_NAME)
                    dist = ((msg[FIELD_EPICENTER_X]-x)**2+(msg[FIELD_EPICENTER_Y]-y)**2)**(1/2)                    
                    if dist < msg[FIELD_RADIUS_B] and dist > msg[FIELD_RADIUS_S]: 
                        # se estiver dentro da area grande e fora da area pequena
                        msg[FIELD_NEXT_HOP] = mcast_addr
                        print (NODE_NAME,"[DENM] << TRAFFIC_JAM in ","x:"+str(msg[FIELD_EPICENTER_X]), "y:"+str(msg[FIELD_EPICENTER_Y]), "("+msg[FIELD_EPICENTER_NAME]+")") 
                    else:   
                        # se estiver fora da area
                        msg[FIELD_NEXT_HOP] = get_next_node_traffic_jam(msg[FIELD_EPICENTER_X],msg[FIELD_EPICENTER_Y],msg[FIELD_RADIUS_S],msg[FIELD_RADIUS_S])
                denm_arr.append(msg)


        for denm in denm_arr:
            denm_arr.remove(denm)
            sock.sendto(json.dumps(denm).encode(), (mcast_addr, port))
            
        # verificar as CAM
            
        if len(messages) > 0:
            msg = messages[0]
            #print (NODE_NAME,"[CAM] << ", msg[FIELD_NAME]) 
            msg[FIELD_NEXT_HOP]  = get_next_node(pos_rsu_x, pos_rsu_y)
            if(msg[FIELD_NEXT_HOP] != IPV6_ADDR):
                messages.remove(msg)
                msg = json.dumps(msg)
                sock.sendto(msg.encode(), (mcast_addr, port))
        
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

        if data[FIELD_ORIGIN] == IPV6_ADDR:
            None # ignora
        elif data[FIELD_TYPE_MSG] == CONNECTION_MSG:
            # Da lista de endereços obter a primeira posicacao referente ao IPv6
            # Verificar se a mensagem que recebeu ja n esta desatualizada
            if data[FIELD_TIMESTAMP] - datetime.timestamp(datetime.now()) < 0.7: 
                # Atualizar/inserir os campos de ultima conexão e de IP                
                # Inserir dados no dicionário
                update_cars_connected(data)            
        elif data[FIELD_TYPE_MSG] == CAM_MSG:
                # print (NODE_NAME,"[CAM] << ", data[FIELD_NAME]) 
                if data[FIELD_ORIGIN] in cars_connected.keys(): 
                    colision_buffer.append(data)                
                # se pacote dirigido a mim vamos reencaminha-lo
                if data[FIELD_NEXT_HOP] == IPV6_ADDR:
                    messages.append(data)
        
        elif data[FIELD_TYPE_MSG] == DENM_MSG:
                if data[DENM_TYPE] == TRAFFIC_JAM:
                        # verificar se carro está dentro a area de alerta
                        # encontrar o próximo nó perto do epicentro e enviar para ele
                        if data[FIELD_NEXT_HOP] == IPV6_ADDR: # se for o proximo no
                            messages.append(data)
                        elif data[FIELD_NEXT_HOP] == mcast_addr:
                            # se tiver sido enviada em multicast
                            print (NODE_NAME,"[DENM] << TRAFFIC_JAM in ","x:"+str(data[FIELD_EPICENTER_X]), "y:"+str(data[FIELD_EPICENTER_Y]), "("+data[FIELD_EPICENTER_NAME]+")") 
                #elif data[FIELD_DEST] == IPV6_ADDR and data[DENM_TYPE] == COLLISION_RISK:
                        #print(NODE_NAME,"[DENM] << COLLISION_RISK with "+data[FIELD_NAME])
                

"""
Esta funcao serve para analisar colisoes iminentes (que vao ocorrer a menos de dois segundos)
a partir da velocidade dos veiculos, calcula-se o tempo para ocorrer a colisao
e é enviada uma DENM para o veiculo com que o carro em questao vai colidir
"""
def analyze_colisions(): 
    last_collision_risks = {}
    while True:
        if len(colision_buffer) > 0:
            msg = colision_buffer[0]

            if msg[FIELD_VELOCITY]:
                node_x = msg[FIELD_POS_X] 
                node_y = msg[FIELD_POS_Y]
                x, y = get_node_location(NODE_NAME) 
                total_velocity = float(msg[FIELD_VELOCITY]+velocity)/3.6
                dist = ((node_x-x)**2+(node_y-y)**2)**(1/2) #calcular a distancia entre nos
                time = dist/total_velocity
                if time > 2:
                    if msg[FIELD_NAME] in last_collision_risks.keys():
                        last_time = last_collision_risks[msg[FIELD_NAME]]
                        if datetime.timestamp(datetime.now()) - last_time > 5:                            
                            last_collision_risks[msg[FIELD_NAME]] = send_denm(msg[FIELD_ORIGIN],msg[FIELD_NAME],COLLISION_RISK) 
                    else:
                        last_collision_risks[msg[FIELD_NAME]] = send_denm(msg[FIELD_ORIGIN],msg[FIELD_NAME],COLLISION_RISK) 

            
            colision_buffer.remove(msg)

"""
funcao para construir uma DENM
"""
def send_denm(dest_ip, dest_name, risk_type):
    msg_denm = {
        FIELD_NAME: NODE_NAME,
        FIELD_ORIGIN: IPV6_ADDR,
        FIELD_DEST: dest_ip,
        FIELD_TYPE_MSG: DENM_MSG, 
        DENM_TYPE: risk_type
    }
    print(NODE_NAME,"[DEMN] >> COLLISION_RISK with "+dest_name)
    sock.sendto(json.dumps(msg_denm).encode(), (mcast_addr, port))

    return datetime.timestamp(datetime.now())

def update_cars_connected(data):
   ip = data[FIELD_ORIGIN]
   if ip == IPV6_ADDR: return
   cars_connected[data[FIELD_ORIGIN]] = data

receive = threading.Thread(target=receive_msg, name="Recived Thread")
send = threading.Thread(target=send_CAM, name="Send Thread")
send_conn = threading.Thread(target=send_connection, name="Send Conn Thread") #enviar mensagens de conexão em multicast
analyze = threading.Thread(target=analyze_connections, name="Analyze Thread")
analyze_col = threading.Thread(target=analyze_colisions, name="Analyze Collions Thread")
forward = threading.Thread(target=forward_msg, name="Forward Thread")

if __name__ == "__main__":
    initCar()
    receive.start()
    send.start()
    send_conn.start()
    analyze_col.start()
    analyze.start()
    forward.start()

    # Aguarda até que ambas as threads terminem
    receive.join()
    send.join()
    send_conn.join()
    analyze_col.join()
    analyze.join()
    forward.join()
