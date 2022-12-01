import socket
import threading
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
    def __init__(self, ip, port):
        super(Node, self).__init__()

        self.ip = ip
        self.port = port
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