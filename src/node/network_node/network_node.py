from .ccoin_protocol import CCoinPackage
from .constants import *

import socket
from typing import List, Callable
import threading
import os

class Conn(threading.Thread):
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

    def __stop_socket(self):
        stop_pkg = CCoinPackage(pkg_type='stop_signal')
        print(stop_pkg.package_data())
        self.sock.send(stop_pkg.package_data())
        # self.send(self.main_node.types['info'], self.main_node.meaning_of_msg['stop_socket'], b'')        
        self.sock.settimeout(None)
        self.sock.close()

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

        self.__stop_socket()
        print('stop')        

    def stop(self):
        self.STOP_FLAG.set()

    def __repr__(self):
        return f'''
        
        NODE INFO
        {self.ip}:{self.port}
        ----------------------------'''
    


class Connection(threading.Thread):
    def __init__(self, ip : str, port : int, sock = None):
        super(Connection, self).__init__()
        self.ip = ip
        self._port = port
        if sock:
            self._sock = sock
        else:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._sock.connect((self.ip, self._port))
        
        self.__sock_timeout = 1.0

        self._sock.settimeout(self.__sock_timeout)

        self.stop_flag = threading.Event()

    def is_alive(self): return not self.stop_flag.is_set()

    def _send_pkg(self, pkg_type, data = b''):
        pkg = CCoinPackage(pkg_type=pkg_type, data=data)

        print(f'Sent to {self.ip}: ', pkg.package_data())
        self._sock.send(pkg.package_data())

    def __stop_socket(self):
        self._send_pkg(pkg_type='stop_signal')
        self._sock.settimeout(None)
        self._sock.close()

    def _handle_package(self, pkg : CCoinPackage):
        pkg_dict = pkg.unpackage_data()

        print('Got: ', pkg_dict)

        if pkg_dict['type'] == 'stop_signal':
            self.stop()

    def run(self):
        while not self.stop_flag.is_set():
            try:
                buff = self._sock.recv(BUF_SIZE)
                
                if buff != b'':
                    message_ended = False
                    
                    while not message_ended:
                        self._sock.settimeout(self.__sock_timeout)
                        
                        try:
                            chunk = self._sock.recv(BUF_SIZE)
                            
                            if not chunk:
                                message_ended = True
                            else:
                                buff += chunk

                        except socket.timeout:
                            message_ended = True

                    self._handle_package(CCoinPackage(got_bytes=buff))
                    
            except socket.timeout:
                continue

            except socket.error as e:
                raise e

        self.__stop_socket()

    def stop(self):
        self.stop_flag.set()

class PeerConnection(Connection):
    def __init__(self, ip, port, blockchain, sock = None):
        super().__init__(ip, port, sock)
        self.blockchain = blockchain

        self.__send_version_pkg()

    def _handle_package(self, pkg : CCoinPackage):
        super()._handle_package(pkg)

        return 
    
    def __send_version_pkg(self):
        chain_len = self.blockchain.get_chain_len()
        version_msg_len = 2
        self._send_pkg('version', int.to_bytes(chain_len, version_msg_len, 'big'))

class ServConnection(Connection):
    def __init__(self, ip, port, init_peers : Callable):
        super().__init__(ip, port)
        self.init_peers = init_peers

    def _handle_package(self, pkg : CCoinPackage):
        super()._handle_package(pkg)
        pkg_dict = pkg.unpackage_data()

        if pkg_dict['type'] == 'peers_ack':
            self.__init_peers(pkg_dict['data'].decode())
        # elif pkg_dict['type'] == '':


        elif pkg_dict['type'] == 'stop_signal':
            self.stop_flag.set()

        return
    
    def __execute_func(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            
            except OSError as e:
                print(e)

        return wrapper


    @__execute_func
    def __init_peers(self, ips_string):
        ips_arr = ips_string.split('\n')
        if ips_arr[0] != '':
            return self.init_peers(ips_arr)


    def peers_request(self):
        self._send_pkg('peers_request', b'')

class NetworkNode(threading.Thread):
    NETWORK_CONF_DIR = '.conf'

    def __init__(self, blockchain):
        super(NetworkNode, self).__init__()

        self.ip = self.__get_local_ip()
        self.port = 9999

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.ip, self.port))
        self.sock.settimeout(1.0)
        self.sock.listen(1)

        self.blockchain = blockchain

        self.peers = []
        self.MAX_CONNECTIONS = 8

        self.STOP_FLAG = threading.Event()

        self.__connect_with_bind_server()

    def __connect_with_bind_server(self):
        if not os.path.exists(NetworkNode.NETWORK_CONF_DIR):
            os.mkdir(NetworkNode.NETWORK_CONF_DIR)
            
            with open(os.path.join(NetworkNode.NETWORK_CONF_DIR, 'bind_server.txt'), 'w') as f:
                pass
            
            raise Exception('[ERROR] Firstly it\'s neccessary to set ip and port of a bind server!!!')
        else:
            with open(os.path.join(NetworkNode.NETWORK_CONF_DIR, 'bind_server.txt'), 'r') as f:
                server_ip, server_port = f.read().split(':')
                self.serv_conn = ServConnection(server_ip, int(server_port), self.init_peers)
                self.serv_conn.start()
                self.serv_conn.peers_request()

        
        # try:
        #     with open(os.path.join(NetworkNode.NETWORK_CONF_DIR, 'bind_server.txt'), 'r') as f:
        #         server_ip, server_port = f.read().split(':')
        #         self.serv_conn = ServConnection(server_ip, server_port)

        #         self.__get_peers()
        # except Exception as e:
        #     print(e)


    def init_peers(self, ips : List[str]):
        for ip in ips:
            self.connect_with_node(ip, self.port)

    def set_bind_server(self, ip, port):
        with open(os.path.join(NetworkNode.NETWORK_CONF_DIR, 'bind_server.txt'), 'w') as f:
            f.write(f'{ip}:{port}')
            self.__connect_with_bind_server()
            self.__get_peers()

        return 'Server was succesfully initialized!'

    def __get_local_ip(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            

            sock.connect(('8.8.8.8', 80))
            print("Got ip ", sock.getsockname()[0])

            return sock.getsockname()[0]
        except socket.error:
            try:
                return socket.gethostbyname(socket.gethostname()) 
            except socket.gaierror:
                return '127.0.0.1'
        finally:
            sock.close()

    def close_connection(self, conn):
        for i in range(len(self.peers)):
            if self.peers[i] == conn:
                del self.peers[i]
                break

    def disconnect_node(self, ip):
        for i in range(len(self.peers)):
            if self.peers[i].ip == ip:
                self.peers[i].stop()
                del self.peers[i]
                break

    def connect_with_node(self, ip, port):
        try:
            for node in self.peers:
                if node.ip == ip:
                    raise ConnectionRefusedError('This host is already connected')

            if len(self.peers) < self.MAX_CONNECTIONS:
                connection = PeerConnection(ip, port, self.blockchain)
                connection.start()
                self.peers.append(connection)

                return connection
            else:
                raise ConnectionRefusedError('MAX CONNECTIONS REACHED!')

        except socket.timeout as e:
            # raise Exception('Peer is unreachable') from None
            raise e

        except Exception as e:
            raise e

    def __send_msg_to_peers(self, type, meaning, data):
        for sock in self.peers:
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
                if len(self.peers) < self.MAX_CONNECTIONS:

                    sock, client_address = self.sock.accept()

                    ip = client_address[0]
                    port = client_address[1]
                    peer = PeerConnection(ip, port, self.blockchain, sock)
                    peer.start()
                    self.peers.append(peer)

                else:
                    print('MAX CONNECTIONS REACHED!')

            except socket.timeout:
                # print('Peers: ', self.peers)
                self.__clear_disconnected_peers()

            except Exception as e:
                raise e

        self.__close_sock()

    def __clear_disconnected_peers(self):
        disconnected_peers = []
        
        for peer in self.peers:
            if not peer.is_alive():
                disconnected_peers.append(peer)


        for peer in disconnected_peers:
            self.peers.remove(peer)

    def __close_sock(self):
        for peer in self.peers:
            peer.stop()
        
        for peer in self.peers:
            peer.join()

        self.serv_conn.stop()

        self.sock.settimeout(None)   
        self.sock.close()


    def getPeers(self): return self.peers

    def __str__(self) -> str:
        return f'''
        HOST INFO
        host_ip: {self.ip}
        host_port: {self.port}
        connections: {self.peers}
        connections: {self.peers}
        '''

    def __repr__(self):
        return f'''
        HOST INFO
        host_ip: {self.ip}
        host_port: {self.port}
        connections: {self.peers}
        connections: {self.peers}
        '''