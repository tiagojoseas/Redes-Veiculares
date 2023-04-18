import json
import socket
from TYPES import *

data = {}
data1 = {}
messages = []

data[FIELD_IP] = 1
data[FIELD_LAST_CONNECTION] = 124312345
data[FIELD_STATUS_CONNECTION] = 0

data1[FIELD_IP] = 1
data1[FIELD_LAST_CONNECTION] = 124312345
data1[FIELD_STATUS_CONNECTION] = 0

messages.append(data)
messages.append(data1)

msg = messages[1]
messages.remove(msg)
msg[FIELD_IP] = 2
msg = json.dumps(msg)
print(msg)
print(messages)