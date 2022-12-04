with open('blockchain/blocks/blk_0001.dat', 'rb') as f:
    print(f.read())

import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(1.0)
sock.connect(('12.12.12.12', 8888))