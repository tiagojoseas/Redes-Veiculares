import json

# Tipos de Nós
RSU = 1
CAR = 2 
TRUCK = 3
MOTORCYCLE = 4
BUS = 5
# Campos JSON

FIELD_NAME = "name"
FIELD_IP = "ip"

FIELD_EPICENTER_X = "epicenter_x"
FIELD_EPICENTER_Y = "epicenter_y"
FIELD_RADIUS_S = "small_radius"
FIELD_RADIUS_B = "big_radius"

#caracteristicas do carro
FIELD_TYPE_NODE = "type_node"
FIELD_VELOCITY = "velocity"
FIELD_WEIGTH = "weigth"
FIELD_HEIGTH = "heigth"
FIELD_LENGTH = "lenght"
FIELD_WIDTH = "width"

#dados dos sensores
FIELD_RAIN = "rain"
FIELD_FOG = "fog"
FIELD_WET_FLOOR = "wet_floor"

FIELD_LAST_CONNECTION = "last_connection"
FIELD_STATUS_CONNECTION = "status_connection"
FIELD_TIMESTAMP = "timeStamp"
FIELD_DEST = "destiny"
FIELD_ORIGIN = "origin"
FIELD_TYPE_MSG = "type_msg"
FIELD_NEXT_HOP = "next_hop" #proximo no a receber a mensagem
FIELD_LAST_HOP = "last_hop" #no anterior
FIELD_POS_X = "x_position" #posição no eixo dos x
FIELD_POS_Y = "y_position" #posição no eixo dos y
FIELD_DEST_X = "x_pos_dest" #posicao do destino eixo x
FIELD_DEST_Y = "y_pos_dest" #posicao do destino eixo y

DENM_TYPE = "dem_type"
COLLISION_RISK = 0 
TRAFFIC_JAM = 1 




CONNECTION_MSG = 0 #tipo de mensagem para manter conexão com vizinhos
CAM_MSG = 1 #tipo de mensagem para enviar dados
DENM_MSG = 2 #mensagem de alerta
#Types Status
STATUS_DISCONNECTED = 0
STATUS_CONNECTED = 1