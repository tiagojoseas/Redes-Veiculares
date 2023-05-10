import socket, json
from datetime import datetime
from TYPES import *

rsu_address = "2001:690:2280:820::2" 
rsu_port = 3000 

R = 15 #15 pixeis = 10 metros
MAX_CARS = 3
dicionario = {}

def start_server(server_address, server_port):
    # Create an IPv6 socket
    sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)

    # Bind the socket to the server address and port
    sock.bind((server_address, server_port))
    while True:
        # Receive data and client address
        data = sock.recvfrom(1024)
        data = json.loads(data)
        dicionario[data[FIELD_IP]] = data
        denm_array = []
        for ip1 in dicionario:
            count_cars = 0
            x1 = dicionario[ip1][FIELD_POS_X]
            y1 = dicionario[ip1][FIELD_POS_Y]
            for ip2 in dicionario:
                if ip1 != ip2:
                    x2 = dicionario[ip2][FIELD_POS_X]
                    y2 = dicionario[ip2][FIELD_POS_Y]
                    dist = ((x2-x1)**2+(y2-y1)**2)**(1/2)
                    if dist < R:
                        count_cars+=count_cars
            if count_cars >= MAX_CARS:
                discard = False
                for demn in denm_array:
                    if demn[FIELD_TIMESTAMP]<60 and (((demn[FIELD_EPICENTER_X]-x1)**2+(demn[FIELD_EPICENTER_Y]-y1)**2)**(1/2)) < (2*R/3):
                        discard = True
                        break
                if not discard:
                    msg_denm = {
                            FIELD_ORIGIN: "2001:690:2280:820::3",
                            FIELD_DEST: "area",
                            FIELD_EPICENTER_X: x1,
                            FIELD_EPICENTER_Y: y1,
                            FIELD_RADIUS_S : R,
                            FIELD_RADIUS_B : 3*R,
                            FIELD_NAME: "servidor",
                            FIELD_TYPE_MSG: DENM_MSG, 
                            DENM_TYPE: TRAFFIC_JAM,
                            FIELD_TIMESTAMP: datetime.now()
                        }
                    denm_array.append(msg_denm)
                    sock.sendto(msg_denm.encode(), (rsu_address, rsu_port))

                        


        print(data[FIELD_NAME])

server_address = "2001:690:2280:820::3" 
server_port = 9999 
start_server(server_address, server_port)
