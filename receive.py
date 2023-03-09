import socket
import struct
import threading

# Endereço de multicast IPv6 e porta
MULTICAST_GROUP = 'ff02::1'
PORT = 3000

# Cria um socket UDP IPv6
sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_JOIN_GROUP,
                socket.inet_pton(socket.AF_INET6, MULTICAST_GROUP))
sock.bind(('::', PORT))
  
while True:
    data, addr = sock.recvfrom(1024)
    print("From " + str(addr) + ": " + data.decode())