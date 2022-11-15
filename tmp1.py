# import sys
# from socket import socket, AF_INET, SOCK_DGRAM

# SERVER_IP   = '192.168.0.123'
# PORT_NUMBER = 5000
# print ("Test client sending packets to IP {0}, via port {1}\n".format(SERVER_IP, PORT_NUMBER))

# mySocket = socket( AF_INET, SOCK_DGRAM )

# f = open('blockchain/blocks/blk_0011.dat', 'rb')
# a = f.read()
# f.close()

# while a:
#     b = input()
#     mySocket.sendto(b'121212',(SERVER_IP,PORT_NUMBER))
# sys.exit()

print(list(bytes.fromhex(hex(int('143055', 16))[2:])))
print(int('123', 16).to_bytes(2, 'little'))
file = f"a.dat"
# f = open(file, 'wb')
f = open(file, 'rb')
# f.write(bytes.fromhex('14ab55'))
print(f.read(1).hex())
f.close()


