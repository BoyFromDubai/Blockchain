import socket
import threading

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
        ----------------------------
        NODE INFO
        {self.ip}:{self.port}
        ----------------------------
        '''


class Server():
    def __init__(self):
        self.ip = self.__get_local_ip()
        self.port = 5000
        self.clients_port = 9999

        self.sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.connections = []

        self.__init_server()
    
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

    def run(self) -> None:
        try:
            while True:
                connection, client_address = self.sock.accept()
                conn_ip = client_address[0]
                conn_port = client_address[1]
                print(conn_ip)
                # print('LEN', len(self.connections))
                connection = Connection(self, connection, conn_ip, conn_port)
                connection.start()
                self.connections.append(connection)



        except (KeyboardInterrupt, EOFError):
            print('Server was stopped by an administrator!')

if __name__ == '__main__':
    server = Server()
    server.run()