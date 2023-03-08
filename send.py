import socket
import struct
import threading

# Endereço de multicast IPv6 e porta
MULTICAST_GROUP = 'ff02::1'
PORT = 3000

# Cria um socket UDP IPv6
sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)

# Configura o socket para permitir o envio de mensagens de multicast
sock.setsockopt(socket.IPPROTO_IPV6, socket.IP_MULTICAST_TTL, 1)



# Função que envia mensagens em um loop
def enviar_mensagens():
    while True:
        # Lê a mensagem a ser enviada do usuário
        message = input('Digite a mensagem a ser enviada: ')
        packed_message = struct.pack('!50s', message.encode())

        # Envia a mensagem para o grupo multicast
        sock.sendto(packed_message, (MULTICAST_GROUP, PORT))

# Função que recebe mensagens em um loop
def receber_mensagens():
    # Configura o socket para receber mensagens de multicast
    sock.bind(('', PORT))
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_JOIN_GROUP, 0)
                    #socket.inet_pton(socket.AF_INET6, MULTICAST_GROUP))
    
    while True:
        data, addr = sock.recvfrom(1024)
        message = struct.unpack('!50s', data)[0].decode().rstrip('\x00')
        print(f'Recebido: {message} de {addr}')

# Cria e inicia as threads de envio e recebimento
envio_thread = threading.Thread(target=enviar_mensagens)
recebimento_thread = threading.Thread(target=receber_mensagens)

envio_thread.start()
recebimento_thread.start()

# Aguarda até que ambas as threads terminem
envio_thread.join()
recebimento_thread.join()
