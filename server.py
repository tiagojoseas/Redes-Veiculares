import socket, json, time
from datetime import datetime
from TYPES import *

rsu_address = "2001:690:2280:820::2"
rsu_port = 9999 

server_address = "2001:690:2280:820::3"
server_port = 9999 

R = 150
MAX_CARS = 2
data_storage = {}
denm_dict = {}
car_conn_time = {}
NODE_NAME = ""

def start_server(server_address, server_port):
    # Create an IPv6 socket
    sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    NODE_NAME = socket.gethostname()
    discard = False
    # Bind the socket to the server address and port
    sock.bind((server_address, server_port))
    while True:
        # Receive data and client address
        data, addr = sock.recvfrom(1024)
        data = json.loads(data.decode())

        try:
            data_storage[data[FIELD_ORIGIN]]
        except: 
            print("SERVER >> New car:",data[FIELD_NAME])

        data_storage[data[FIELD_ORIGIN]] = data
        car_conn_time[data[FIELD_ORIGIN]] = datetime.timestamp(datetime.now())

        for ip1 in data_storage:
            count_cars = 1
            x1 = data_storage[ip1][FIELD_POS_X]
            y1 = data_storage[ip1][FIELD_POS_Y]

            for ip2 in data_storage:    #conta o numero de carro a uma distancia < que R do ip1
                
                if ip1 != ip2:
                    x2 = data_storage[ip2][FIELD_POS_X]
                    y2 = data_storage[ip2][FIELD_POS_Y]
                    dist = ((x2-x1)**2+(y2-y1)**2)**(1/2)

                    if dist < R:
                        count_cars+=1


            if count_cars >= MAX_CARS:
                #try: denm_dict[ip1]
                #except: denm_dict[ip1] = [0,0,0]

                if denm_dict:
                    for key in denm_dict:
                        if(key != ip1):
                            if ((denm_dict[key][FIELD_EPICENTER_X]-x1)**2+(denm_dict[key][FIELD_EPICENTER_Y]-y1)**2)**(1/2) < (R/3) and datetime.timestamp(datetime.now())-car_conn_time[key] < 30 :
                                discard = True
                                break
                
                
                if not discard:
                    msg_denm = {
                        FIELD_ORIGIN: server_address,
                        FIELD_EPICENTER_X: x1,
                        FIELD_EPICENTER_Y: y1,
                        FIELD_EPICENTER_NAME: data_storage[ip1][FIELD_NAME],
                        FIELD_RADIUS_S : R,
                        FIELD_RADIUS_B : 3*R,
                        FIELD_NAME: NODE_NAME,
                        FIELD_TYPE_MSG: DENM_MSG, 
                        DENM_TYPE: TRAFFIC_JAM,
                        FIELD_TIMESTAMP: datetime.timestamp(datetime.now())
                    }
                    denm_dict[ip1] = msg_denm
                    print("SERVER >> TRAFFIC_JAM",data_storage[ip1][FIELD_NAME],x1, y1,datetime.now(), count_cars)
                    sock.sendto(json.dumps(msg_denm).encode(), (rsu_address, rsu_port))

                discard = False    
               

if __name__ == "__main__":
    start_server(server_address, server_port)
