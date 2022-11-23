import socket
import threading
import os

# class Sender():
#     def __init__(self, host_ip) -> None:
#         self.header_size = 64
#         self.ip = host_ip
#         self.port = 9999
#         self.server_of_peers_port = 5000

#         self.peers_request = 'peers'
#         self.msg_format = 'utf-8'
#         self.disconnect_message = 'DISCONNECTED'

#         try:
#             with open('network/server.txt', 'r') as f:
#                 self.server_of_peers_ip = f.read()
#         except:
#             self.server_of_peers_ip = None

#         thread_ask_for_peers = threading.Thread(target=self.__ask_for_peers, args=())
#         thread_ask_for_peers.start()

#     def __ask_for_peers(self):
#         for_peers_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         server_of_peers_addr = (self.server_of_peers_ip, self.server_of_peers_port)
#         for_peers_socket.connect(server_of_peers_addr)

#         msg = self.peers_request.encode(self.msg_format)
#         msg_len = str(len(msg)).encode(self.msg_format)
#         msg_len += b' ' * (self.header_size - len(msg_len))
#         for_peers_socket.send(msg_len)
#         for_peers_socket.send(msg)


    

# class Receiver():
#     def __init__(self, host_ip):
#         self.ip = host_ip
#         self.port = 9999

#         self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.server.bind((self.ip, self.port))

#         self.listening_thread = threading.Thread(target=self.__start_listening, args=())
#         self.listening_thread.start()

    

# class Client():
#     def __init__(self):
#         self.ip_addr = self.__get_local_ip()
#         self.client = Sender(self.ip_addr)
#         self.server = Receiver(self.ip_addr)

#     def __get_local_ip(self):
#         try:
#             sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#             # Use Google Public DNS server to determine own IP
#             sock.connect(('8.8.8.8', 80))

#             return sock.getsockname()[0]
#         except socket.error:
#             try:
#                 return socket.gethostbyname(socket.gethostname()) 
#             except socket.gaierror:
#                 return '127.0.0.1'
#         finally:
#             sock.close()

class Client():
    def __init__(self):
        self.host_ip = self.__get_local_ip()
        self.listening_port = 9999
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind( (self.host_ip, self.listening_port) )

        try:
            with open('network/server.txt', 'r') as f:
                self.peers_server_ip = f.read()
        except:
            self.peers_server_ip = None
        
        self.peers_server_port = 5000

        self.header_size = 64
        self.msg_type = 64
        self.msg_format = 'utf-8'
        self.disconnect_message = 'DISCONNECTED'

        peers_thread = threading.Thread(target=self.__ask_for_peers)
        peers_thread.start()

        listening_thread = threading.Thread(target=self.__start_listening)
        listening_thread.start()

    def __ask_for_peers(self):
        msg = 'peers_request'
        self.__send_msg_to_peers_server(msg)

    def __diconnection_message_to_peers_server(self):
        msg = 'DISCONNECTED'
        self.__send_msg_to_peers_server(msg)
            
    def __send_msg_to_peers_server(self, msg):
        for_peers_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_of_peers_addr = (self.peers_server_ip, self.peers_server_port)
        for_peers_socket.connect(server_of_peers_addr)

        msg = msg.encode(self.msg_format)
        msg_len = str(len(msg)).encode(self.msg_format)
        msg_len += b' ' * (self.header_size - len(msg_len))
        for_peers_socket.send(msg_len)
        for_peers_socket.send(msg)
        
    def __get_message(self, conn, addr):
        msg_length = conn.recv(self.header_size).decode(self.msg_format)
        
        if msg_length:
            msg_length = int(msg_length)
            print(msg_length)
            msg_type = conn.recv(self.msg_type) 
            print(msg_type)
            msg = conn.recv(msg_length)
            print(msg)

            if msg_type == 'peers_answer':
                self.__diconnection_message_to_peers_server()

    def changeServerToConnectWith(self, ip_addr):
        with open('network/server.txt', 'w') as f:
            f.write(ip_addr)
        self.peers_server_port = ip_addr

    def __start_listening(self):

        self.server.listen()

        while True:
            (conn, addr) = self.server.accept()
            thread = threading.Thread(target=self.__get_message, args=(conn, addr))
            thread.start()

        # self.app_closed = False

        # self.ip_addr = self.__get_local_ip()
        # self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # self.port = 9999
        # self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.server_of_peers_port = 5000
        # self.server.bind((self.ip_addr, self.port))
        # self.server.settimeout(2)
        
        # self.listening_thread = threading.Thread(target=self.__start_listening, args=())
        # self.listening_thread.start()

        # try:
        #     with open('network/server.txt', 'r') as f:
        #         self.server_to_ask_for_peers = f.read()
        # except:
        #     self.server_to_ask_for_peers = None
        
        # self.peers = self.__get_peers()

    # def closeListening(self):
    #     self.app_closed = True
    #     # self.client.connect((self.ip_addr, self.port))
    #     # self.client.send(''.encode())

    # def __start_listening(self):
    #     while not self.app_closed:
    #         try:
    #             msg = self.server.recv(1024)
    #         except socket.timeout as e:
    #             err = e.args[0]
    #             print(err)
    #             if err == 'timed out' and not self.app_closed:
    #                 continue
    #             else:
    #                 self.server.close()
    
    # def __get_peers(self):
    #     print((self.server_to_ask_for_peers, self.server_of_peers_port))
    #     self.client.connect((self.server_to_ask_for_peers, self.server_of_peers_port))

    #     self.client.send('peers'.encode())

    #     return []

    # def changeServerToConnectWith(self, ip_addr):
    #     with open('network/server.txt', 'w') as f:
    #         f.write(ip_addr)
    #     self.server_to_ask_for_peers = ip_addr

    # def __send_part_of_chain(self, last_peer_got_block_index):
    #     files_arr = sorted(os.listdir('blockchain/blocks'))
        
    #     for file in files_arr:
    #         # TODO: check this if later when sending will be ready
    #         if int(file[-4]) < last_peer_got_block_index:
    #             continue 
    #         f = open('blockchain/blocks/' + file, 'rb')
    #         block_data = f.read()
    #         thread_sending = threading.Thread(target=self.sendBlock, args=(block_data,))
    #         f.close()
    #     pass

    # def sendBlock(self, block_data):

    #     data = 'block_file'.encode()
    #     data += block_data
    #     data += 'END'.encode()
    #     socket.send
    #     pass    

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
    

        
        