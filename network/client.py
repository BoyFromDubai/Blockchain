import socket
import threading
import os

class Connection(threading.Thread):
    def __init__(self, main_node, sock, ip, port, blockchain):
        super(Connection, self).__init__()
        self.ip = ip
        self.port = port
        self.sock = sock
        self.sock.settimeout(1.0)
        self.STOP_FLAG = threading.Event()
        
        self.blockcain = blockchain

        self.TYPE_FIELD_OFFSET = 0
        self.MEANING_OF_MSG_OFFSET = 1
        self.SIZE_FIELD_OFFSET = 9
        self.MSG_FIELD_OFFSET = 25

        self.main_node = main_node

    def send(self, type, meaning, data):
        packet = self.__create_packet(type, meaning, data)
        self.sock.send(packet)

    def __create_packet(self, type, meaning, data):
        msg = b''
        msg += type
        msg += meaning
        msg += len(data).to_bytes(self.MSG_FIELD_OFFSET-self.SIZE_FIELD_OFFSET, 'big')
        msg += data

        return msg
    
    def __answer(self, meaning):
        version_request = self.main_node.meaning_of_msg['version']

        match meaning:
            case version_request:
                self.__msg_verack()

    def __answer_version(self):
        height = len(os.listdir('blockchain/blocks')).to_bytes(4, 'big')
        self.send(self.main_node.types['info'], self.main_node.meaning_of_msg['version'], height)

        


    def __get(self, meaning, msg):
        version_answer = self.main_node.meaning_of_msg['version']

        match meaning:
            case version_answer:
                self.__get_inv(msg)

    def __get_inv(self, msg):
        if int.from_bytes(msg, 'big') < self.blockcain.getChainLen():
            print(15555)




    def run(self):
        while not self.STOP_FLAG.is_set():
            try:    # print(12)
                buff = b''
                header = self.sock.recv(self.MSG_FIELD_OFFSET)
                
                if header != b'':
                    type = header[self.TYPE_FIELD_OFFSET:self.MEANING_OF_MSG_OFFSET]
                    msg_meaning = header[self.MEANING_OF_MSG_OFFSET:self.SIZE_FIELD_OFFSET]
                    size = int.from_bytes(header[self.SIZE_FIELD_OFFSET:self.MSG_FIELD_OFFSET], 'big')
                    print(type)
                    print(msg_meaning)
                    print(size)

                    if type == self.main_node.types['request']:
                        self.__answer(msg_meaning)
                    
                    else:
                        read_size = 1024

                        for i in range(0, size, read_size):
                            if size - i > read_size:
                                buff += self.sock.recv(read_size)
                            else:
                                buff += self.sock.recv(size - i)

                        self.__get(msg_meaning, buff)

                        print(f'MESSAGE from {self.ip}')
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
    def __init__(self, ip, port, blockchain):
        super(Node, self).__init__()

        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__init_server()
        self.blockchain = blockchain
        
        self.connections = []
        self.MAX_CONNECTIONS = 8

        self.STOP_FLAG = threading.Event()
        self.types = {
            'info': b'\x00',
            'request': b'\x01',
        }

        self.meaning_of_msg = {
            'version': b'\x00\x00\x00\x00\x00\x00\x00\x00',
            'verack': b'\x00\x00\x00\x00\x00\x00\x00\x01',
        }

    def __init_server(self):
        self.sock.bind((self.ip, self.port))
        self.sock.settimeout(1.0)
        self.sock.listen(1)

    def connectWithNode(self, ip, port):
        try:
            for node in self.connections:
                if node.ip == ip:
                    raise ConnectionRefusedError('This host is already connected')

            if len(self.connections) < self.MAX_CONNECTIONS:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((ip, port))
                thread = Connection(self, sock, ip, port, self.blockchain)
                thread.start()
                self.connections.append(thread)
            else:
                raise ConnectionRefusedError('MAX CONNECTIONS REACHED!')

        except Exception as e:
            raise e


    def sendMsgToAllNodes(self, type, meaning, data):
        for sock in self.connections:
            sending_thread = threading.Thread(target=sock.send, args=(type, meaning, data))
            sending_thread.start()

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
                    print(conn_ip)
                    sock = Connection(self, connection, conn_ip, conn_port, self.blockchain)
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