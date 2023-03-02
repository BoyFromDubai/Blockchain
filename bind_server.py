import socket
import threading
from src.node.network_node import CCoinPackage, constants, Connection
import os

class PeerConnection(Connection):
    def __init__(self, ip, port, sock):
        super().__init__(ip, port, sock)

    def _handle_package(self, data):
        pkg = CCoinPackage(got_bytes=data)
        print('Got: ', data)
        pkg_dict = pkg.unpackage_data()
        if pkg_dict['type'] == 'peers_request':
            self.__send_active_peers('peers_ack')
        # elif pkg_dict['type'] == '':


        elif pkg_dict['type'] == 'send_stop_signal':
            self.stop_flag.set()

        return

    def __send_active_peers(self, pkg_type):
        with open(Server.PEERS_FILE_PATH, 'r') as f:
            ips = f.read().splitlines()
            ips.remove(self.ip)
            res = b''
            
            for ip in ips:
                res += (ip + '\n').encode()

            self._send_pkg(pkg_type, res)        


    def peers_request(self):
        self._send_pkg('peers_request', b'')

class Server():
    PEERS_FILE_PATH = 'peers.txt'

    def __init__(self):
        if not os.path.exists(self.PEERS_FILE_PATH):
            with open(self.PEERS_FILE_PATH, 'w'):
                pass

        self.__ip = self.__get_local_ip()
        self.__port = 5000

        self.__sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.__peers = []

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
        self.__sock.bind((self.__ip, self.__port))
        self.__sock.settimeout(1.0)
        self.__sock.listen(1)

    def __stop_server(self):
        self.__sock.settimeout(None)   
        self.__sock.close()

        return 'Server was stopped by an administrator!'
    
    def __append_connection(self, sock, ip, port):
        peer = PeerConnection(ip, port, sock)
        peer.start()
        self.__peers.append(peer)

        with open(Server.PEERS_FILE_PATH, 'r+') as f:
            # ips = f.readlines()
            ips = f.read().splitlines()

            if ip in ips:
                print(ips)
            else:
                f.write(ip + '\n')

    def __remove_disconnected_node_from_file(self, ip):
        with open(self.PEERS_FILE_PATH, "r") as f:
            lines = f.read().splitlines()
        with open(self.PEERS_FILE_PATH, "w") as f:
            for line in lines:
                if line != ip:
                    f.write(line + '\n')

    def __clear_disconnected_peers(self):
        disconnected_peers = []
        
        for peer in self.__peers:
            if not peer.is_alive():
                disconnected_peers.append(peer)
                self.__remove_disconnected_node_from_file(peer.ip)


        for peer in disconnected_peers:
            self.__peers.remove(peer)


    def __listen_for_connection(self):
        sock, client_address = self.__sock.accept()
        
        print(f'{client_address[0]} connected')
        self.__append_connection(sock, client_address[0], client_address[1])

    def run(self) -> None:
        while True:
            try:
                self.__listen_for_connection()

            except socket.timeout:
                self.__clear_disconnected_peers()

            except (KeyboardInterrupt, EOFError):
                self.__stop_server()
                break

    def __repr__(self) -> str:
        return f'''
        Server listening on {self.__ip}:{self.__port}
        '''

if __name__ == '__main__':
    server = Server()
    print(server)
    server.run()