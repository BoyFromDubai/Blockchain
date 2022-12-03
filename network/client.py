import socket
import threading
import os

class Connection(threading.Thread):
    def __init__(self, main_node, sock, ip, port, debug_print):
        super(Connection, self).__init__()
        self.ip = ip
        self.port = port
        self.sock = sock
        self.sock.settimeout(1.0)
        self.STOP_FLAG = threading.Event()

        self.debug_print = debug_print

        self.TYPE_FIELD_OFFSET = 0
        self.MEANING_OF_MSG_OFFSET = 1
        self.SIZE_FIELD_OFFSET = 9
        self.MSG_FIELD_OFFSET = 25

        self.CHAIN_LEN_SIZE = 2 

        self.main_node = main_node

        self.__send_version_msg()

    def send(self, type, meaning, data):
        packet = self.__create_packet(type, meaning, data)
        print('PRINT')
        print(packet)
        print()
        self.sock.send(packet)

    def __create_packet(self, type, meaning, data):
        msg = b''
        msg += type
        msg += meaning
        msg += len(data).to_bytes(self.MSG_FIELD_OFFSET-self.SIZE_FIELD_OFFSET, 'big')
        msg += data

        return msg
    


    def __answer(self, request_msg_meaning):
        version_request = self.main_node.meaning_of_msg['version']

        # if request_msg_meaning == self.main_node.meaning_of_msg['version']:
            # self.__send_version_msg()

        if request_msg_meaning == self.main_node.meaning_of_msg['get_blocks']:
            self.__answer_get_blocks_msg()
        else:
            pass

    def __send_version_msg(self):
        height = len(os.listdir('blockchain/blocks')).to_bytes(4, 'big')
        self.send(self.main_node.types['info'], self.main_node.meaning_of_msg['version'], height)
    def __answer_get_blocks_msg(self):
        self.send(self.main_node.types['info'], self.main_node.meaning_of_msg['get_blocks'], b'\x07\x07')
    
        


    def __get(self, info_msg_meaning, msg):
        
        if info_msg_meaning == self.main_node.meaning_of_msg['version']:
            self.__get_version_msg(msg)
        elif info_msg_meaning == self.main_node.meaning_of_msg['get_blocks']:
            pass
        elif info_msg_meaning == self.main_node.meaning_of_msg['stop_socket']:
            self.__kill_socket()
        else:
            pass
        # match meaning:
        #     case 1:
        #         pass
        #     case version_answer:
        #         pass
        #     case _:
        #         pass
            # case version_answer:
            # case get_blocks_answer:
                # pass 
        
    def __get_version_msg(self, msg):
        chain_len = self.main_node.getChainLen()
        print()
        print(chain_len.to_bytes(self.CHAIN_LEN_SIZE, 'big'))
        print()

        if int.from_bytes(msg, 'big') > chain_len:
            self.send(self.main_node.types['request'], self.main_node.meaning_of_msg['get_blocks'], chain_len.to_bytes(self.CHAIN_LEN_SIZE, 'big'))
            # self.send(self.main_node.types['request'], self.main_node.meaning_of_msg['get_blocks'], b'')

    def __get_msg(self):
        
        pass

    def __stop_peer_socket(self):
        self.send(self.main_node.types['info'], self.main_node.meaning_of_msg['stop_socket'], b'')

    def __kill_socket(self):
        self.main_node.close_connection(self)
    
    def __parse_header(self, header):
        msg_type = header[self.TYPE_FIELD_OFFSET:self.MEANING_OF_MSG_OFFSET]
        msg_meaning = header[self.MEANING_OF_MSG_OFFSET:self.SIZE_FIELD_OFFSET]
        size = int.from_bytes(header[self.SIZE_FIELD_OFFSET:self.MSG_FIELD_OFFSET], 'big')

        return (msg_type, msg_meaning, size)

    def run(self):
        while not self.STOP_FLAG.is_set():
            try:
                buff = b''
                header = self.sock.recv(self.MSG_FIELD_OFFSET)
                
                if header != b'':
                    msg_type, msg_meaning, size = self.__parse_header(header)

                    print('GOT')
                    for key, item in self.main_node.types.items():
                        if item == msg_type:
                            print(key)
                    print(msg_type)

                    for key, item in self.main_node.meaning_of_msg.items():
                        if item == msg_meaning:
                            print(key)
                    print(msg_meaning)
                        

                    print(size)

                    if msg_type == self.main_node.types['request']:
                        self.__answer(msg_meaning)
                    
                    else:
                        read_size = 1024

                        if read_size > size:
                            buff += self.sock.recv(size)
                        
                        else:
                            for i in range(0, size, read_size):
                                if size - i > read_size:
                                    buff += self.sock.recv(read_size)
                                else:
                                    buff += self.sock.recv(size - i)

                        self.__get(msg_meaning, buff)

                        print(f'MESSAGE from {self.ip} of meaning {msg_meaning}')
                        print(buff)
                        print()
                    # buff += chunk

            except socket.timeout:
                continue

            except socket.error as e:
                raise e

        self.__stop_peer_socket()        
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
    def __init__(self, ip, port, blockchain, debug_print = False):
        super(Node, self).__init__()

        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__init_server()

        self.debug_print = debug_print
        self.blockchain = blockchain
        # self.chain_len = blockchain.getChainLen()

        self.connections = []
        self.MAX_CONNECTIONS = 8

        self.STOP_FLAG = threading.Event()

        self.types = {
            'info': b'\x00',
            'request': b'\x01',
        }
        self.meaning_of_msg = {
            'version': b'\x00\x00\x00\x00\x00\x00\x00\x00',
            'get_blocks': b'\x00\x00\x00\x00\x00\x00\x00\x01',

            'stop_socket': b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF',
        }

    def getChainLen(self): return self.blockchain.getChainLen()

    def __init_server(self):
        self.sock.bind((self.ip, self.port))
        self.sock.settimeout(1.0)
        self.sock.listen(1)

    def close_connection(self, conn):
        for i in range(len(self.connections)):
            if self.connections[i] == conn:
                del self.connections[i]
                break

    def connectWithNode(self, ip, port):
        try:
            for node in self.connections:
                if node.ip == ip:
                    raise ConnectionRefusedError('This host is already connected')

            if len(self.connections) < self.MAX_CONNECTIONS:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((ip, port))
                connection = Connection(self, sock, ip, port, self.debug_print)
                connection.start()
                self.connections.append(connection)
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
                    # print('LEN', len(self.connections))
                    connection = Connection(self, connection, conn_ip, conn_port, self.debug_print)
                    connection.start()
                    self.connections.append(connection)

                else:
                    print('MAX CONNECTIONS REACHED!')

                # for conn in self.connections:
                    # Basic information exchange (not secure) of the id's of the nodes!
            except socket.timeout:
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