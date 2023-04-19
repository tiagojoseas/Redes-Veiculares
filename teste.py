import json
import socket
from TYPES import *

sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
sock.connect(('2001:4860:4860::8888', 1))
IP = socket.getsockname()[0]
print(IP)
print(socket.getaddrinfo(socket.gethostname), None, socket.AF_INET6)
name = socket.gethostname()
ip = socket.gethostbyname(name)
socket.gethostname()
print(ip)