import threading
import socket
import time

class Connection(threading.Thread):
    def __init__(self, sock, ip, port):
        super(Connection, self).__init__()
        self.ip = ip
        self.port = port
        self.sock = sock
        self.sock.settimeout(1.0)
        self.STOP_FLAG = threading.Event()

        self.TYPE_FIELD_OFFSET = 0
        self.SIZE_FIELD_OFFSET = 8
        self.MSG_FIELD_OFFSET = 24

    def send(self, type, data):
        packet = self.__create_packet(type, data)
        self.sock.send(packet)

    def __create_packet(self, type, data):
        msg = b''
        msg += type
        msg += len(data).to_bytes(self.MSG_FIELD_OFFSET-self.SIZE_FIELD_OFFSET, 'big')
        msg += data

        return msg

    def run(self):
        while not self.STOP_FLAG.is_set():
            try:    # print(12)
                buff = b''
                header = self.sock.recv(self.MSG_FIELD_OFFSET)
                
                if header != b'':
                    type = header[self.TYPE_FIELD_OFFSET:self.SIZE_FIELD_OFFSET]
                    size = int.from_bytes(header[self.SIZE_FIELD_OFFSET:self.MSG_FIELD_OFFSET], 'big')
                    print(type)
                    print(size)

                    read_size = 1024

                    for i in range(0, size, read_size):
                        if size - i > read_size:
                            buff += self.sock.recv(read_size)
                        else:
                            buff += self.sock.recv(size - i)

                    print(f'MESSAGE from {self.port}')
                    print(buff)
                    # buff += chunk

            except socket.timeout:
                continue

            except socket.error as e:
                raise e
        # print("ALMOST KILLED")
        self.sock.settimeout(None)   
        self.sock.close()

    def stop(self):
        self.STOP_FLAG.set()


    def __repr__(self):
        return f'''
        
        node info
        node_ip: {self.ip}
        node_port: {self.port}
        ----------------------------'''

class Node(threading.Thread):
    def __init__(self, ip, port, name):
        super(Node, self).__init__()

        self.ip = ip
        self.port = port
        self.name = name
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__init_server()
        
        self.connections = []
        self.MAX_CONNECTIONS = 8

        self.STOP_FLAG = threading.Event()

 

    def __init_server(self):
        self.sock.bind((self.ip, self.port))
        self.sock.settimeout(1.0)
        self.sock.listen(1)

    def connectWithNode(self, ip, port):
        if len(self.connections) < self.MAX_CONNECTIONS:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ip, port))
            thread = Connection(sock, ip, port)
            thread.start()
            self.connections.append(thread)
        else:
            print('MAX CONNECTIONS REACHED!')

    def sendMsgToAllNodes(self, type, data):
        for sock in self.connections:
            sock.send(type, data)

    def stop(self):
        self.STOP_FLAG.set()        

    def run(self):

        while not self.STOP_FLAG.is_set():
            try:
                if len(self.connections) < self.MAX_CONNECTIONS:

                    connection, client_address = self.sock.accept()

                    # print(connection)
                    conn_ip = client_address[0] # backward compatibilty
                    conn_port = client_address[1] # backward compatibilty
                    sock = Connection(connection, conn_ip, conn_port)
                    sock.start()
                    self.connections.append(sock)
                else:
                    print('MAX CONNECTIONS REACHED!')

                # for conn in self.connections:
                #     print(conn.port, self.name)
                    # Basic information exchange (not secure) of the id's of the nodes!
            except socket.timeout:
                # print(12)
                continue

            except Exception as e:
                raise e
            
        for node in self.connections:
            node.stop()

        for node in self.connections:
            node.stop()
        
        for node in self.connections:
            node.join()

        self.sock.settimeout(None)   
        self.sock.close()

    def __repr__(self):
        return f'''
        HOST INFO
        host_ip: {self.ip}
        host_port: {self.port}
        connections: {self.connections}
        connections: {self.connections}'''



node1 = Node("127.0.0.1", 5001, 'node1')
node1.start()
node2 = Node("127.0.0.1", 5002, 'node2')
node2.start()
node3 = Node("127.0.0.1", 5003, 'node3')
node3.start()

node2.connectWithNode("127.0.0.1", 5003)
# node2.connectWithNode("127.0.0.1", 5001)

# node3.connectWithNode("127.0.0.1", 5001)
# node3.connectWithNode("127.0.0.1", 5002)
# node1.connectWithNode("127.0.0.1", 5003)

node2.sendMsgToAllNodes(b'\x01\x02\x03\x04\x01\x02\x03\x04', b'\x01\x02\x03\x04\x05\x06\x07\x08\x09\x10\x01\x02\x03\x04\x05\x06\x07\x08\x09\x10\x01\x02\x03\x04\x05\x06\x07\x08\x09\x10\x01\x02\x03\x04\x05\x06\x07\x08\x09\x10\x01\x02\x03\x04\x05\x06\x07\x08\x09\x10\x01\x02\x03\x04\x05\x06\x07\x08\x09\x10\x01\x02\x03\x04\x05\x06\x07\x08\x09\x10\x01\x02\x03\x04\x05\x06\x07\x08\x09\x10\x01\x02\x03\x04\x05\x06\x07\x08\x09\x10\x01\x02\x03\x04\x05\x06\x07\x08\x09\x10\x01\x02\x03\x04\x05\x06\x07\x08\x09\x10')
node2.sendMsgToAllNodes(b'\x01\x02\x03\x04\x01\x02\x03\x04', b'\x10\x09\x08\x07\x06\x05\x04\x03\x02\x01')
node3.sendMsgToAllNodes(b'\x01\x02\x03\x04\x01\x02\x03\x04', b'\x00\x02\x04\x06\x08\x10\x12\x14\x16\x18')

# print(node2)
# print('=====v======')
# print(node1)
# print('=====v======')
# print(node3)

node1.stop()
node2.stop()
node3.stop()
