from ..node import Node
import threading
from queue import Queue
import time

class OutputThread(threading.Thread):
    def __init__(self, output_queue, prefix) -> None:
        super().__init__()
        self.__prefix = prefix
        self.__output_queue = output_queue
        self.__stop_flag = threading.Event()

    def run(self):
        while not self.__stop_flag.isSet():
            time.sleep(1)

            if not self.__output_queue.empty():
                print()
                print(self.__output_queue.get())
                print()
                print(self.__prefix, end='', flush=True)

    def stop(self):
        self.__stop_flag.set()

class ConsoleUser:
    def __init__(self) -> None:
        self.__username = 'ccoin_client'
        self.__prefix = self.__username + ': '
        self.__node = Node()
        self.__res_values = Queue()
        self.__processes = []

        self.__start_output()

    def start_input(self):

        while True:
            try:
                print(self.__prefix, end='')
                command = input()
                commands_arr = command.split(' ')

                if not commands_arr:
                    print('Command must not be empty!')
                    continue          

                elif commands_arr[0] == 'mine':
                    if len(commands_arr) > 1 and commands_arr[1] == '-o':
                        self.__execute_func(func=self.__node.mine_block)

                elif commands_arr[0] == 'list':
                    if len(commands_arr) > 1 and commands_arr[1] == 'db':
                        self.__execute_func(self.__node.get_db_utxos)
                    if len(commands_arr) > 1 and commands_arr[1] == 'utxos':
                        self.__execute_func(self.__node.get_my_utxos)
                    if len(commands_arr) > 1 and commands_arr[1] == 'peers':
                        self.__execute_func(self.__node.get_peers)
                
                elif commands_arr[0] == 'show':
                    if len(commands_arr) > 1 and commands_arr[1] == 'ip':
                        self.__execute_func(self.__node.get_ip)
                    if len(commands_arr) > 1 and commands_arr[1] == 'chain':
                        if len(commands_arr) > 2 and commands_arr[2] == 'len':
                            self.__execute_func(self.__node.get_chain_len)
                            
                elif commands_arr[0] == 'set':
                    if len(commands_arr) > 1 and commands_arr[1] == 'server':
                        if len(commands_arr[2].split(':')) == 2:
                            ip, port = commands_arr[2].split(':')
                            self.__execute_func(self.__node.set_bind_server, ip, port)

                        else:
                            self.__res_values.put('[ERROR] Address syntax is incorrect!')

                elif commands_arr[0] == 'vin':
                    if len(commands_arr) > 2:
                        self.__node.append_to_vins((commands_arr[1], commands_arr[2]))

                elif commands_arr[0] == 'vout':
                    if len(commands_arr) > 2:
                        self.__node.append_to_vouts((commands_arr[1], commands_arr[2]))

                elif commands_arr[0] == 'commit':
                    if len(commands_arr) > 1 and commands_arr[1] == 'tx':
                        self.__execute_func(self.__node.create_tx)

            except (KeyboardInterrupt, EOFError):
                for process in self.__processes:
                    process.stop()

                del self.__node

                break;
    
    def __update_queue(func):
        def wrapper(*args, **kwargs):
            res = func(*args, **kwargs)
            
            if res:
                args[0].__res_values.put(res)

        return wrapper

    def __append_process(func):
        def wrapper(*args, **kwargs):
            args[0].__processes.append(func(*args, **kwargs))
        
        return wrapper

    @__update_queue
    def __execute_func(self, func, *args):
        # try:
        #     return func(*args)
        # except Exception as e:
        #     return e

        return func(*args)

    @__append_process
    def __start_output(self):
        self.__output_process = OutputThread(self.__res_values, self.__prefix)
        self.__output_process.start()

        return self.__output_process

    def __del__(self):
        for process in self.__processes:
            process.stop()

# def complete(text,state):
#     volcab = ['dog','cat','rabbit','bird','slug','snail']
#     results = [x for x in volcab if x.startswith(text)] + [None]
#     return results[state]

# readline.set_completer(complete)