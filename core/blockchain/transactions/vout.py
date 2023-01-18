from core.blockchain.constants import *
import math

class Vout():
    def __init__(self, address, value) -> None:
        self.vout_data = self.__create_vout(address, value)

    def __create_vout(self, address, value):
        
        vout_data = int(value).to_bytes(BLOCK_STRUCT['value'], "little")
        print(address)
        script_pub_key = int(address, 16).to_bytes(math.ceil(len(address) / 2), 'big') 
        vout_data += len(script_pub_key).to_bytes(BLOCK_STRUCT['script_sig_size'], "little") #ScriptPubKey size
        vout_data += script_pub_key #ScriptPubKey

        return vout_data