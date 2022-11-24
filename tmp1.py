import threading

class AA(threading.Thread):
    def a(self):
        print(threading.current_thread().name)

print(threading.current_thread().name)
a = AA()
a.a()