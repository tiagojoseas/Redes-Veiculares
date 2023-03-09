import socket
import struct
import threading

# Endereço de multicast IPv6 e porta
MULTICAST_GROUP = 'ff02::1'
PORT = 3000

# Cria um socket UDP IPv6
sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)



while True:
    # Lê a mensagem a ser enviada do usuário
    message = input('Digite a mensagem a ser enviada: ')

    # Envia a mensagem para o grupo multicast
    sock.sendto(message.encode(), (MULTICAST_GROUP, PORT))


