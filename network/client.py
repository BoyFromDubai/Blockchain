import socket
import threading
import os

class Client():
    def __init__(self):
        self.app_closed = False
        self.ip_addr = self.__get_local_ip()
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.port = 9999
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.server.setblocking(False)
        self.server_of_peers_port = 5000
        
        self.listening_thread = threading.Thread(target=self.__start_listening)
        self.listening_thread.start()
        # self.__start_listening()

        try:
            with open('network/server.txt', 'r') as f:
                self.server_to_ask_for_peers = f.read()
        except:
            self.server_to_ask_for_peers = None
        
        self.peers = self.__get_peers()

    def closeListening(self):
        self.app_closed = True
        self.client.connect((self.ip_addr, self.port))
        self.client.send(''.encode())

    def __start_listening(self):
        while True and not self.app_closed:
            print(self.ip_addr)
            self.server.bind((str(self.ip_addr), self.port))
            # self.server.listen()
            # client, data = self.server.accept()
            # self.server.settimeout(1)

            (data, addr) = self.server.recvfrom(1024)
            print(data)
            # self.client.listen()
        pass
    
    def __get_peers(self):
        self.client.connect((self.server_to_ask_for_peers, self.server_of_peers_port))

        self.client.send('peers'.encode())

        return []

    def changeServerToConnectWith(self, ip_addr):
        with open('network/server.txt', 'w') as f:
            f.write(ip_addr)
        self.server_to_ask_for_peers = ip_addr

    def __send_part_of_chain(self, last_peer_got_block_index):
        files_arr = sorted(os.listdir('blockchain/blocks'))
        
        for file in files_arr:
            # TODO: check this if later when sending will be ready
            if int(file[-4]) < last_peer_got_block_index:
                continue 
            f = open('blockchain/blocks/' + file, 'rb')
            block_data = f.read()
            thread_sending = threading.Thread(target=self.sendBlock, args=(block_data,))
            f.close()
        pass

    def sendBlock(self, block_data):

        data = 'block_file'.encode()
        data += block_data
        data += 'END'.encode()
        socket.send
        pass

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
    

        
        