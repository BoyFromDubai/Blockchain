import socket
import threading
import os

class Connection(threading.Thread):
    CHAIN_LEN_SIZE = 2 
    def __init__(self, main_node, sock, ip, port, blockchain, debug_print):
        super(Connection, self).__init__()
        self.ip = ip
        self.port = port
        self.sock = sock
        self.sock.settimeout(1.0)
        self.STOP_FLAG = threading.Event()

        self.blockchain = blockchain

        self.debug_print = debug_print

        self.TYPE_FIELD_OFFSET = 0
        self.MEANING_OF_MSG_OFFSET = 1
        self.SIZE_FIELD_OFFSET = 9
        self.MSG_FIELD_OFFSET = 25

        self.HASH_OF_BLOCK_SIZE = 32 

        self.main_node = main_node

        self.__send_version_msg()
        # self.__answer_get_blocks_msg()

    def send(self, type, meaning, data):
        packet = self.__create_packet(type, meaning, data)
        print('SEND')
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
    
    def __answer(self, request_msg_meaning, msg):

        if request_msg_meaning == self.main_node.meaning_of_msg['get_blocks']:
            self.__answer_get_blocks_msg(msg)
        elif request_msg_meaning == self.main_node.meaning_of_msg['last_block_id']:
            self.__start_sending_blk_hashes(int.from_bytes(msg, 'big'))
        else:
            pass

    def __send_version_msg(self):
        height = len(os.listdir('blockchain/blocks')).to_bytes(4, 'big')
        self.send(self.main_node.types['info'], self.main_node.meaning_of_msg['version'], height)
    
    def __answer_get_blocks_msg(self, msg):
        blk_to_start_with = int.from_bytes(msg, 'big')
        chain_len = self.blockchain.get_chain_len()
        
        for i in range(blk_to_start_with, chain_len):
            data = i.to_bytes(self.CHAIN_LEN_SIZE, 'big')
            print('ith block')
            print(i.to_bytes(self.CHAIN_LEN_SIZE, 'big'))
            data += self.blockchain.get_nth_block(i)
            self.send(self.main_node.types['info'], self.main_node.meaning_of_msg['block'], data)

    def __start_sending_blk_hashes(self, n):
        self.sock.send(self.blockchain.hash_nth_block_in_digest(n-1))
        answer = self.sock.recv(1)
        print('answer')
        print(answer)
        if int.from_bytes(answer, 'big'):
            self.__start_sending_blk_hashes(n-1)

    def __get(self, info_msg_meaning, msg):
        
        if  info_msg_meaning == self.main_node.meaning_of_msg['version']:
            self.__get_version_msg(msg)
        elif  info_msg_meaning ==  self.main_node.meaning_of_msg['last_block_id']:
            self.__get_last_block_info_msg(msg)
        elif  info_msg_meaning ==  self.main_node.meaning_of_msg['block']:
            self.__get_blocks_msg(msg)
        elif info_msg_meaning == self.main_node.meaning_of_msg['tx']:
            self.__get_tx_msg(msg)
        elif info_msg_meaning == self.main_node.meaning_of_msg['stop_socket']:
            self.__kill_socket()
        else:
            pass

    def __get_version_msg(self, msg):
        chain_len = self.blockchain.get_chain_len()
        print('chain_len')
        print(chain_len)

        if int.from_bytes(msg, 'big') > chain_len:
            self.send(self.main_node.types['request'], self.main_node.meaning_of_msg['last_block_id'], chain_len.to_bytes(self.CHAIN_LEN_SIZE, 'big'))
            self.__start_getting_blk_hashes(chain_len)

    def __get_blocks_msg(self, msg):
        print(msg)
        file_num = msg[:self.CHAIN_LEN_SIZE]
        blk_data = msg[self.CHAIN_LEN_SIZE:]
        print('get_blk_msgs')
        print(file_num)
        # self.blockchain.getNewBlockFromPeer(int.from_bytes(file_num, 'big'), blk_data)

    def __start_getting_blk_hashes(self, n):
        his_hash = self.sock.recv(self.HASH_OF_BLOCK_SIZE)
        my_hash = self.blockchain.hash_nth_block_in_digest(n-1)
        print(f'asking for {n-1}')

        if his_hash == my_hash:
            self.sock.send((0).to_bytes(1, 'big'))
            blk_to_start_with = n.to_bytes(self.CHAIN_LEN_SIZE, 'big')
            # msg += n.to_bytes(self.CHAIN_LEN_SIZE, 'big')
            self.send(self.main_node.types['request'], self.main_node.meaning_of_msg['get_blocks'], blk_to_start_with)
        else:
            self.sock.send((1).to_bytes(1, 'big'))
            self.__start_getting_blk_hashes(n-1)

    
    def __get_tx_msg(self, msg):
        try:
            self.blockchain.verifyTransaction(msg)
        except Exception as e:
            print(e)

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
                    print('Header')
                    print(header)
                    print('------------')
                    for key, item in self.main_node.types.items():
                        if item == msg_type:
                            print(key)

                    for key, item in self.main_node.meaning_of_msg.items():
                        if item == msg_meaning:
                            print(key)
                            x = key
                    print(size)
                    print('------------')
                    print()

                    read_size = 1024

                    if read_size > size:
                        buff += self.sock.recv(size)
                    
                    else:
                        for i in range(0, size, read_size):
                            if size - i > read_size:
                                buff += self.sock.recv(read_size)
                            else:
                                buff += self.sock.recv(size - i)

                    if msg_type == self.main_node.types['request']:

                        self.__answer(msg_meaning, buff)
                    
                    else:

                        self.__get(msg_meaning, buff)

                    print(f'MESSAGE from {self.ip} of meaning {x}')
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
        
        NODE INFO
        {self.ip}:{self.port}
        ----------------------------'''

class NetworkNode(threading.Thread):
    NETWORK_CONF_DIR = '.conf'

    def __init__(self, blockchain):
        super(NetworkNode, self).__init__()

        self.ip = self.__get_local_ip()
        self.port = 9999
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__init_server()

        self.__init_bind_server()

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
            'get_blocks': b'\x00\x00\x00\x00\x00\x00\x00\x01',
            'block': b'\x00\x00\x00\x00\x00\x00\x00\x02',
            'tx': b'\x00\x00\x00\x00\x00\x00\x00\x03',
            'last_block_id': b'\x00\x00\x00\x00\x00\x00\x00\x04',

            'stop_socket': b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF',
        }

    def __init_bind_server(self):
        if not os.path.exists(NetworkNode.NETWORK_CONF_DIR):
            os.mkdir(NetworkNode.NETWORK_CONF_DIR)
        
        try:
            with open(os.path.join(NetworkNode.NETWORK_CONF_DIR, 'bind_server.txt'), 'r') as f:
                server_ip, server_port = f.read().split(':')
                self.__get_peers(server_ip, server_port)
        except:
            pass

    def __get_peers(self, ip, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))

    def set_bind_server(self, ip, port):
        with open(os.path.join(NetworkNode.NETWORK_CONF_DIR, 'bind_server.txt'), 'w') as f:
            f.write(f'{ip}:{port}')

        return 'Server was succesfully initialized!'

    def __get_local_ip(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            sock.connect(('8.8.8.8', 80))

            return sock.getsockname()[0]
        except socket.error:
            try:
                return socket.gethostbyname(socket.gethostname()) 
            except socket.gaierror:
                return '127.0.0.1'
        finally:
            sock.close()

    def __init_server(self):
        self.sock.bind((self.ip, self.port))
        self.sock.settimeout(1.0)
        self.sock.listen(1)

    def close_connection(self, conn):
        for i in range(len(self.connections)):
            if self.connections[i] == conn:
                del self.connections[i]
                break

    def disconnect_node(self, ip):
        print(self.connections)
        for i in range(len(self.connections)):
            print(i)
            if self.connections[i].ip == ip:
                self.connections[i].stop()
                del self.connections[i]
                break

    def connect_with_node(self, ip, port):
        try:
            print(self.connections)
            for node in self.connections:
                if node.ip == ip:
                    raise ConnectionRefusedError('This host is already connected')

            if len(self.connections) < self.MAX_CONNECTIONS:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2.0)
                sock.connect((ip, port))
                connection = Connection(self, sock, ip, port, self.blockchain, self.debug_print)
                connection.start()
                self.connections.append(connection)

                return connection
            else:
                raise ConnectionRefusedError('MAX CONNECTIONS REACHED!')

        except socket.timeout as e:
            # raise Exception('Peer is unreachable') from None
            raise e

        except Exception as e:
            raise e

    def __send_msg_to_peers(self, type, meaning, data):
        for sock in self.connections:
            sending_thread = threading.Thread(target=sock.send, args=(type, meaning, data))
            sending_thread.start()

    def stop(self):
        self.STOP_FLAG.set()

    def new_block_message(self, blk_info):
        msg = (self.blockchain.get_chain_len() - 1).to_bytes(Connection.CHAIN_LEN_SIZE, 'big') + blk_info
        self.__send_msg_to_peers(self.types['info'], self.meaning_of_msg['block'], msg)

    def newTxMessage(self, tx_data):
        self.__send_msg_to_peers(self.types['info'], self.meaning_of_msg['tx'], tx_data)

    def run(self):

        while not self.STOP_FLAG.is_set():
            try:
                if len(self.connections) < self.MAX_CONNECTIONS:

                    connection, client_address = self.sock.accept()

                    conn_ip = client_address[0]
                    conn_port = client_address[1]
                    print(conn_ip)
                    # print('LEN', len(self.connections))
                    connection = Connection(self, connection, conn_ip, conn_port, self.blockchain, self.debug_print)
                    connection.start()
                    self.connections.append(connection)

                else:
                    print('MAX CONNECTIONS REACHED!')

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

    def getPeers(self): return self.connections

    def __str__(self) -> str:
        return f'''
        HOST INFO
        host_ip: {self.ip}
        host_port: {self.port}
        connections: {self.connections}
        connections: {self.connections}
        '''

    def __repr__(self):
        return f'''
        HOST INFO
        host_ip: {self.ip}
        host_port: {self.port}
        connections: {self.connections}
        connections: {self.connections}
        '''