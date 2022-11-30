import threading
import socket

def send(from_sock, to_ip, to_port, data):
    from_sock.connect((to_ip, to_port))
    from_sock.send(data)

def listen(node):
    node.listen()
    data, addr = node.accept()
    print(data)

node1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
node1.bind(("127.0.0.1", 5000))
thread1 = threading.Thread(target=listen, args=node1)
thread1.start()
node2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# node2.bind(("127.0.0.1", 5001))
thread2 = threading.Thread(target=send, args=(node2, "127.0.0.1", 5000, 'asdf'))
thread2.start()
node3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# node3.bind(("127.0.0.1", 5002))
thread3 = threading.Thread(target=send, args=(node3, "127.0.0.1", 5000, 'asdf'))
thread3.start()
