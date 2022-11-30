import socket
import threading

class Node(threading.Thread):
    def __init__(self, host, port):
        super(Node, self).__init__()

        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen(3)

        # self.inbound_connections = []
        self.outbound_connections = []
        self.MAX_CONNECTIONS = 8

        self.STOP_FLAG = False

    # def __init_server(self):

    def run(self):
        self.sock.accept()
        while not self.STOP_FLAG:
            connection, client_address = self.sock.accept()

            self.debug_print("Total inbound connections:" + str(len(self.nodes_inbound)))
            # When the maximum connections is reached, it disconnects the connection 
            if self.max_connections == 0 or len(self.nodes_inbound) < self.max_connections:
                connected_ip = client_address[0] # backward compatibilty
                print()
                
                # Basic information exchange (not secure) of the id's of the nodes!
class Connection(threading.Thread):
    def __init__(self):
        super(Connection).__init__()
