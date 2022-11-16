import socket
import threading

class Client():
    def __init__(self):
        self.IPAddr=self.__get_local_ip()
        self.server_to_ask_for_peers = ''
        try:
            with open('server.txt', 'r') as f:
                self.server_to_ask_for_peers = f.read()
        except:
            self.server_to_ask_for_peers = None
        self.peers = []

    def __get_local_ip(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # Use Google Public DNS server to determine own IP
            sock.connect(('8.8.8.8', 80))

            return sock.getsockname()[0]
        except socket.error:
            try:
                return socket.gethostbyname(socket.gethostname()) 
            except socket.gaierror:
                return '127.0.0.1'
        finally:
            sock.close()

    def changeServerToConnectWith(self, ip_addr):
        with open('network/server.txt', 'w') as f:
            f.write(ip_addr)
        self.server_to_ask_for_peers = ip_addr

    def sendData(self):
        pass

    

        
        