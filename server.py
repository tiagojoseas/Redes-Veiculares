import socket, json
from TYPES import *

R = 
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
        dicionario[data[FIELD_IP]]=data
        for ip1 in dicionario:
            x = dicionario[ip1][FIELD_POS_X]
            y = dicionario[ip1][FIELD_POS_Y]
            for ip2 in dicionario:


        print(data[FIELD_NAME])

server_address = "2001:690:2280:820::3" 
server_port = 9999 
start_server(server_address, server_port)
