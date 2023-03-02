import socket
import threading
from src.node.network_node import CCoinPackage, constants
import os

class Connection(threading.Thread):
    def __init__(self, main_node, sock, ip, port):
        super(Connection, self).__init__()
        self.ip = ip
        self.port = port
        self.sock = sock
        self.sock_timeout = 1.0
        self.sock.settimeout(self.sock_timeout)
        self.STOP_FLAG = threading.Event()

        self.main_node = main_node
        # self.__answer_get_blocks_msg()

    def __stop_peer_socket(self):
        self.send(self.main_node.types['info'], self.main_node.meaning_of_msg['stop_socket'], b'')

    def __send_pkg(self, pkg_type, data):
        pkg = CCoinPackage(pkg_type = pkg_type, data = data)
        print("Sent: ", pkg.package_data())
        self.sock.send(pkg.package_data())

    def __send_active_peers(self, pkg_type):
        with open(Server.PEERS_FILE_PATH, 'r') as f:
            ips = f.read().splitlines()
            ips.remove(self.ip)
            res = b''
            
            for ip in ips:
                res += (ip + '\n').encode()

            self.__send_pkg(pkg_type, res)        
        

    def __handle_data(self, data: dict):
        print(data)
        if data['type'] == 'ask_for_peers':
            self.__send_active_peers('send_peers')

    def run(self):
        while not self.STOP_FLAG.is_set():
            try:
                buff = self.sock.recv(constants.BUF_SIZE)
                
                if buff != b'':
                    message_ended = False
                    
                    while not message_ended:
                        self.sock.settimeout(self.sock_timeout)
                        
                        try:
                            data = self.sock.recv(constants.BUF_SIZE)
                            buff += data
                        except socket.timeout:
                            message_ended = True

                    print(buff)
                                            
                    package = CCoinPackage(got_bytes=buff)
                    self.__handle_data(package.unpackage_data())

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
    PEERS_FILE_PATH = 'peers.txt'

    def __init__(self):
        if not os.path.exists(self.PEERS_FILE_PATH):
            with open(self.PEERS_FILE_PATH, 'w'):
                pass

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

    def __stop_server(self):
        self.sock.settimeout(None)   
        self.sock.close()

        return 'Server was stopped by an administrator!'
    

    def __append_connection(self, connection, ip, port):
        connection = Connection(self, connection, ip, port)
        connection.start()
        self.connections.append(connection)

        with open(Server.PEERS_FILE_PATH, 'r+') as f:
            # ips = f.readlines()
            ips = f.read().splitlines()

            if ip in ips:
                print(ips)
            else:
                f.write(ip + '\n')

    def run(self) -> None:
        while True:
            try:
                connection, client_address = self.sock.accept()
                
                print(f'{client_address[0]} connected')
                self.__append_connection(connection, client_address[0], client_address[1])

            except socket.timeout:
                continue

            except (KeyboardInterrupt, EOFError):
                self.__stop_server()
                break

    def __repr__(self) -> str:
        return f'''
        Server listening on {self.ip}:{self.port}
        '''

if __name__ == '__main__':
    server = Server()
    print(server)
    server.run()