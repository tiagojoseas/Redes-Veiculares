import socket
from TYPES import *

data = {}
messages = {}

data[FIELD_IP] = 1
data[FIELD_LAST_CONNECTION] = 124312345
data[FIELD_STATUS_CONNECTION] = 0

messages[2220] = data
print(messages)

data[FIELD_IP] = 1
data[FIELD_LAST_CONNECTION] = 12431234456788
data[FIELD_STATUS_CONNECTION] = 0

messages[2220] = data

del messages[2220]

print(messages)