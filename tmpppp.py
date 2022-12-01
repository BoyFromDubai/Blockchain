import socket
import time
import threading
import random
import hashlib
import json

class NodeConnection(threading.Thread):

    def __init__(self, main_node, sock, host, port):

        super(NodeConnection, self).__init__()

        self.host = host
        self.port = port
        self.main_node = main_node
        self.sock = sock
        self.terminate_flag = threading.Event()

        self.sock.settimeout(10.0)

    def send(self, data, encoding_type='utf-8'):

        if isinstance(data, str):
            try:
                self.sock.sendall( data.encode(encoding_type) )

            except Exception as e: # Fixed issue #19: When sending is corrupted, close the connection
                self.main_node.debug_print("nodeconnection send: Error sending data to node: " + str(e))
                self.stop() # Stopping node due to failure

        elif isinstance(data, dict):
            try:
                self.sock.sendall(json.dumps(data).encode(encoding_type))

            except TypeError as type_error:
                self.main_node.debug_print('This dict is invalid')
                self.main_node.debug_print(type_error)

            except Exception as e: # Fixed issue #19: When sending is corrupted, close the connection
                self.main_node.debug_print("nodeconnection send: Error sending data to node: " + str(e))
                self.stop() # Stopping node due to failure

        elif isinstance(data, bytes):
            try:
                self.sock.sendall(data)

            except Exception as e: # Fixed issue #19: When sending is corrupted, close the connection
                self.main_node.debug_print("nodeconnection send: Error sending data to node: " + str(e))
                self.stop() # Stopping node due to failure

        else:
            self.main_node.debug_print('datatype used is not valid plese use str, dict (will be send as json) or bytes')

    def stop(self):
        self.terminate_flag.set()

    def parse_packet(self, packet):
        try:
            packet_decoded = packet.decode('utf-8')

            try:
                return json.loads(packet_decoded)

            except json.decoder.JSONDecodeError:
                return packet_decoded

        except UnicodeDecodeError:
            return packet

    def run(self):
        buffer = b'' # Hold the stream that comes in!

        while not self.terminate_flag.is_set():
            chunk = b''

            try:
                chunk = self.sock.recv(4096) 

            except socket.timeout:
                self.main_node.debug_print("NodeConnection: timeout")

            except Exception as e:
                self.terminate_flag.set() # Exception occurred terminating the connection
                self.main_node.debug_print('Unexpected error')
                self.main_node.debug_print(e)

            if chunk != b'':
                buffer += chunk

                self.main_node.message_count_recv += 1
                self.main_node.node_message( self, self.parse_packet(chunk) )

            time.sleep(0.01)

        self.sock.settimeout(None)
        self.sock.close()
        self.main_node.node_disconnected( self ) # Fixed issue #19: Send to main_node when a node is disconnected. We do not know whether it is inbounc or outbound.
        self.main_node.debug_print("NodeConnection: Stopped")

    def __str__(self):
        return 'NodeConnection: {}:{} <-> {}:{} ({})'.format(self.main_node.host, self.main_node.port, self.host, self.port)

    def __repr__(self):
        return '<NodeConnection: Node {}:{} <-> Connection {}:{}>'.format(self.main_node.host, self.main_node.port, self.host, self.port)


class Node(threading.Thread):

    def __init__(self, host, port, callback=None, max_connections=0):
        super(Node, self).__init__()

        self.terminate_flag = threading.Event()

        self.host = host
        self.port = port

        self.callback = callback

        self.nodes_inbound = []  # Nodes that are connect with us N->(US)

        self.nodes_outbound = []  # Nodes that we are connected to (US)->N

        self.reconnect_to_nodes = []

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.init_server()

        self.message_count_send = 0
        self.message_count_recv = 0
        self.message_count_rerr = 0
        
        self.max_connections = max_connections

        self.SIZE_FIELD = 16
        self.MSG_TYPE_FIELD = 32

        self.debug = False

    @property
    def all_nodes(self):
        return self.nodes_inbound + self.nodes_outbound
    
    def outboundNodes(self):
        return self.nodes_outbound
    
    def inboundNodes(self):
        return self.nodes_inbound

    def debug_print(self, message):
        if self.debug:
            print("DEBUG (" + self.port + "): " + message)

    def init_server(self):
        print("Initialisation of the Node on port: " + str(self.port) + " on node ("")")
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.settimeout(1.0)
        self.sock.listen(1)

    def print_connections(self):
        print("Node connection overview:")
        print("- Total nodes connected with us: %d" % len(self.nodes_inbound))
        print("- Total nodes connected to     : %d" % len(self.nodes_outbound))

    def send_to_nodes(self, data, exclude=[]):
        self.message_count_send += 1

        for n in self.nodes_outbound:
            if n in exclude:
                self.debug_print("Node send_to_nodes: Excluding node in sending the message")
            else:
                self.send_to_node(n, data)

    def send_to_node(self, n, data):
        self.message_count_send = self.message_count_send + 1
        if n in self.nodes_inbound or n in self.nodes_outbound:
            n.send(data)

        else:
            self.debug_print("Node send_to_node: Could not send the data, node is not found!")

    def connect_with_node(self, host, port, reconnect=False):

        if host == self.host and port == self.port:
            print("connect_with_node: Cannot connect with yourself!!")
            return False
        # Check if node is already connected with this node!
        for node in self.nodes_outbound:
            if node.host == host and node.port == port:
                print("connect_with_node: Already connected with this node (" ").")
                return True

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.debug_print("connecting to %s port %s" % (host, port))
            sock.connect((host, port))

            thread_client = self.create_new_connection(sock, host, port)
            thread_client.start()

            self.nodes_outbound.append(thread_client)
            self.outbound_node_connected(thread_client)

            # If reconnection to this host is required, it will be added to the list!
            if reconnect:
                self.debug_print("connect_with_node: Reconnection check is enabled on node " + host + ":" + str(port))
                self.reconnect_to_nodes.append({
                    "host": host, "port": port, "tries": 0
                })

            return True

        except Exception as e:
            self.debug_print("TcpServer.connect_with_node: Could not connect with node. (" + str(e) + ")")
            return False

    def disconnect_with_node(self, node):
        if node in self.nodes_outbound:
            self.node_disconnect_with_outbound_node(node)
            node.stop()

        else:
            self.debug_print("Node disconnect_with_node: cannot disconnect with a node with which we are not connected.")

    def stop(self):
        """Stop this node and terminate all the connected nodes."""
        self.node_request_to_stop()
        self.terminate_flag.set()

    def create_new_connection(self, connection, host, port):
        return NodeConnection(self, connection, host, port)

    def reconnect_nodes(self):
        for node_to_check in self.reconnect_to_nodes:
            found_node = False
            self.debug_print("reconnect_nodes: Checking node " + node_to_check["host"] + ":" + str(node_to_check["port"]))

            for node in self.nodes_outbound:
                if node.host == node_to_check["host"] and node.port == node_to_check["port"]:
                    found_node = True
                    node_to_check["trials"] = 0 # Reset the trials
                    self.debug_print("reconnect_nodes: Node " + node_to_check["host"] + ":" + str(node_to_check["port"]) + " still running!")

            if not found_node: # Reconnect with node
                node_to_check["trials"] += 1
                if self.node_reconnection_error(node_to_check["host"], node_to_check["port"], node_to_check["trials"]):
                    self.connect_with_node(node_to_check["host"], node_to_check["port"]) # Perform the actual connection

                else:
                    self.debug_print("reconnect_nodes: Removing node (" + node_to_check["host"] + ":" + str(node_to_check["port"]) + ") from the reconnection list!")
                    self.reconnect_to_nodes.remove(node_to_check)

    def run(self):
        while not self.terminate_flag.is_set():  # Check whether the thread needs to be closed
            try:
                self.debug_print("Node: Wait for incoming connection")
                connection, client_address = self.sock.accept()

                self.debug_print("Total inbound connections:" + str(len(self.nodes_inbound)))
                if self.max_connections == 0 or len(self.nodes_inbound) < self.max_connections:
                    
                    connected_node_port = client_address[1] # backward compatibilty

                    thread_client = self.create_new_connection(connection, client_address[0], connected_node_port)
                    thread_client.start()

                    self.nodes_inbound.append(thread_client)
                    self.inbound_node_connected(thread_client)

                else:
                    self.debug_print("New connection is closed. You have reached the maximum connection limit!")
                    connection.close()
            
            except socket.timeout:
                self.debug_print('Node: Connection timeout!')

            except Exception as e:
                raise e

            self.reconnect_nodes()

            time.sleep(0.01)

        print("Node stopping...")
        for t in self.nodes_inbound:
            t.stop()

        for t in self.nodes_outbound:
            t.stop()

        time.sleep(1)

        for t in self.nodes_inbound:
            t.join()

        for t in self.nodes_outbound:
            t.join()

        self.sock.settimeout(None)   
        self.sock.close()
        print("Node stopped")

    def outbound_node_connected(self, node):
        self.debug_print("outbound_node_connected: ")
        if self.callback is not None:
            self.callback("outbound_node_connected", self, node, {})

    def inbound_node_connected(self, node):
        self.debug_print("inbound_node_connected: ")
        if self.callback is not None:
            self.callback("inbound_node_connected", self, node, {})

    def node_disconnected(self, node):
        self.debug_print("node_disconnected: ")

        if node in self.nodes_inbound:
            del self.nodes_inbound[self.nodes_inbound.index(node)]
            self.inbound_node_disconnected(node)

        if node in self.nodes_outbound:
            del self.nodes_outbound[self.nodes_outbound.index(node)]
            self.outbound_node_disconnected(node)

    def inbound_node_disconnected(self, node):
        self.debug_print("inbound_node_disconnected: ")
        if self.callback is not None:
            self.callback("inbound_node_disconnected", self, node, {})

    def outbound_node_disconnected(self, node):
        self.debug_print("outbound_node_disconnected: ")
        if self.callback is not None:
            self.callback("outbound_node_disconnected", self, node, {})

    def node_message(self, node, data):
        print(data)
        self.debug_print("node_message: " + ": " + str(data))

    def node_disconnect_with_outbound_node(self, node):
        self.debug_print("node wants to disconnect with oher outbound node: ")
        if self.callback is not None:
            self.callback("node_disconnect_with_outbound_node", self, node, {})

    def node_request_to_stop(self):
        self.debug_print("node is requested to stop!")
        if self.callback is not None:
            self.callback("node_request_to_stop", self, {}, {})

    def node_reconnection_error(self, host, port, trials):
        self.debug_print("node_reconnection_error: Reconnecting to node " + host + ":" + str(port) + " (trials: " + str(trials) + ")")
        return True

    def __str__(self):
        return 'Node: {}:{}'.format(self.host, self.port)

    def __repr__(self):
        return '<Node {}:{} id: {}>'.format(self.host, self.port)
    

node1 = Node("127.0.0.1", 5001)
node1.start()
node2 = Node("127.0.0.1", 5002)
node2.start()
node3 = Node("127.0.0.1", 5003)
node3.start()

node1.connect_with_node("127.0.0.1", 5003)

node1.send_to_nodes(b'12')

node1.stop()
node2.stop()
node3.stop()