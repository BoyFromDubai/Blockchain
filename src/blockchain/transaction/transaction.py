from ..blockchain import BLOCK_STRUCT
import math
from typing import List

class Vin:
    def __init__(self, blockchain, secret_key, txid: bytes, vout_num: int) -> None:
        self.blockchain = blockchain
        self.secret_key = secret_key
        self.__create_vin(txid, vout_num)

    def __create_vin(self, txid: bytes, vout_num: int):
        txid = int(txid, 16).to_bytes(BLOCK_STRUCT['txid'], 'big')

        utxo_data = self.blockchain.chainstate_db.get_info_of_utxo_digest(txid, vout_num)

        if int.from_bytes(utxo_data['spent'], 'little'):
            raise ValueError('[ERROR] Vout is already spent!!!')
        else:
            script_pub_key = utxo_data['script_pub_key'] 
            
            vin_data = txid 
            vin_data += vout_num.to_bytes(BLOCK_STRUCT['vout'], "little")

            message_to_sign = txid
            script_sig = self.secret_key.sign(message_to_sign)
            
            if not self.blockchain.confirm_sign(script_sig, script_pub_key, message_to_sign):
                raise ValueError('[ERROR] Signature failed!')

            vin_data += len(script_sig).to_bytes(BLOCK_STRUCT['script_sig_size'], "little") #ScriptSig size
            vin_data += script_sig #ScriptSig

            self.vin = vin_data

class Vout:
    def __init__(self, address: str, value: str) -> None:
        self.__create_vout(address, value)

    def __create_vout(self, address: str, value: str):

        vout_data = int(value).to_bytes(BLOCK_STRUCT['value'], "little")

        script_pub_key = int(address, 16).to_bytes(math.ceil(len(address) / 2), 'big') 
        vout_data += len(script_pub_key).to_bytes(BLOCK_STRUCT['script_sig_size'], "little") #ScriptPubKey size
        vout_data += script_pub_key #ScriptPubKey

        self.vout = vout_data

class Transaction:
    
    def __init__(self, vout_data: List[tuple], vin_data: List[tuple] = [], blockchain = None, secret_key = None) -> None:
        self.blockchain = blockchain
        self.secret_key = secret_key
        self.tx_data = self.__create_tx(vout_data, vin_data)

    def __create_tx(self, vout_data: List[tuple], vin_data: List[tuple]):
        tx_data = (0).to_bytes(BLOCK_STRUCT['version'], "little") #version
        tx_data += len(vin_data).to_bytes(BLOCK_STRUCT['input_count'], "little") #input_count

        for i in range(len(vin_data)):
            tx_data += Vin(self.blockchain, self.secret_key, vin_data[i][0], int(vin_data[i][1])).vin

        tx_data += len(vout_data).to_bytes(1, "little") #outputs num

        for i in range(len(vout_data)):
            tx_data += Vout(vout_data[i][0], int(vout_data[i][1])).vout

        return tx_data
