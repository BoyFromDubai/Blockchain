from ..node import Node
from multiprocessing import Process, Queue
import time
import os

class OutputProcess(Process):
    def __init__(self, output_queue, prefix) -> None:
        super().__init__()
        self.prefix = prefix
        self.output_queue = output_queue

    def run(self):
        while True:
            time.sleep(1)

            if not self.output_queue.empty():
                print()
                print(self.output_queue.get())
                print()
                print(self.prefix, end='', flush=True)

class ConsoleUser:
    HISTORY_DIR = 'history'
    HISTORY_PATH = 'history/history.txt'

    def __init__(self) -> None:
        self.__username = 'ccoin_client'
        self.prefix = self.__username + ': '
        self.__processes = []
        self.res_values = Queue()
        self.node = Node()

        self.__start_output()

    def start_input(self):

        while True:
            try:
                print(self.prefix, end='')
                command = input()
                commands_arr = command.split(' ')
                # self.res_values.put(12)

                if not commands_arr:
                    print('Command must not be empty!')
                    continue          

                if commands_arr[0] == 'mine':

                    if len(commands_arr) > 1 and commands_arr[1] == '-o': 
                        self.__execute_func(func=self.node.mine_block)               
                        continue

                if commands_arr[0] == 'list':
                    if len(commands_arr) > 1 and commands_arr[1] == 'db':
                        self.__execute_func(self.node.get_db_utxos)
                    if len(commands_arr) > 1 and commands_arr[1] == 'utxos':
                        self.__execute_func(self.node.get_my_utxos)
                    if len(commands_arr) > 1 and commands_arr[1] == 'peers':
                        self.__execute_func(self.node.get_peers)
                
                if commands_arr[0] == 'show':
                    if len(commands_arr) > 1 and commands_arr[1] == 'ip':
                        self.__execute_func(self.node.get_ip)
                    if len(commands_arr) > 1 and commands_arr[1] == 'chain':
                        if len(commands_arr) > 2 and commands_arr[2] == 'len':
                            self.__execute_func(self.node.get_chain_len)
                            
                    
                
                if commands_arr[0] == 'set':
                    if len(commands_arr) > 1 and commands_arr[1] == 'server':
                        self.__execute_func(self.node.set_bind_server, commands_arr[2], commands_arr[3]) 

                if commands_arr[0] == 'vin':
                    if len(commands_arr) > 2:
                        self.node.append_to_vins((commands_arr[1], commands_arr[2]))

                if commands_arr[0] == 'vout':
                    if len(commands_arr) > 2:
                        self.node.append_to_vouts((commands_arr[1], commands_arr[2]))

                if commands_arr[0] == 'commit':
                    if len(commands_arr) > 1 and commands_arr[1] == 'tx':
                        self.__execute_func(self.node.create_tx)
                        
                        vins_info = []
                        vouts_info = []

            except (KeyboardInterrupt, EOFError) as e:
                for process in self.__processes:
                    process.terminate()

                del self.node

                break;
    
    def __update_queue(func):
        def wrapper(*args, **kwargs):
            args[0].res_values.put(func(*args, **kwargs))

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
        self.output_process = OutputProcess(self.res_values, self.prefix)
        self.output_process.start()

        return self.output_process

    def __del__(self):
        for process in self.__processes:
            process.terminate()

# def complete(text,state):
#     volcab = ['dog','cat','rabbit','bird','slug','snail']
#     results = [x for x in volcab if x.startswith(text)] + [None]
#     return results[state]

# readline.set_completer(complete)