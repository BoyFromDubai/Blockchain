import plyvel
import hashlib
from ..blockchain import NUMS_IN_NAME

from typing import List

class ChainStateDB:
    TX_LETTER = 'c'
    
    KEY_STRUCT = {
        'letter':       1,
        'hash_len':     32,
        'index_len':    1,
        'index':        None,
    }
    
    UTXO_STRUCT = {
        'coinbase':             1,
        'height':               4,
        'spent':                1, 
        'spent_by':             32, 
        'value':                8, 
        'script_pub_key_size':  8,
        'script_pub_key':       None, 
    }

    def __init__(self, blockchain) -> None:
        self.db = plyvel.DB('chainstate/', create_if_missing=True)
        self.blockchain = blockchain

    def __del__(self):
        self.db.close()

    def __count_byte_length(self, number: int): return (number.bit_length() + 7) // 8

    def __spend_utxo(self, txid_to_spend: bytes, vout: int, txid_of_spending_tx: bytes):
        key = self.__create_key(txid_to_spend, vout)
        utxo = self.db.get(key)
        
        cur_offset = self.__get_utxo_property_offset('spent')
        updated_utxo = utxo[:cur_offset]
        
        cur_offset += self.UTXO_STRUCT['spent']
        updated_utxo += (1).to_bytes(self.UTXO_STRUCT['spent'], 'little')
        
        cur_offset += self.UTXO_STRUCT['spent_by']
        updated_utxo += txid_of_spending_tx
        
        updated_utxo += utxo[cur_offset:]

        self.db.delete(key)
        self.db.put(key, updated_utxo)

        return txid_to_spend, vout

    def update_db(self, tx_info: bytes):
        vins = self.blockchain.get_vins(tx_info)
        spent_utxo = []
        spending_txid = hashlib.sha256(tx_info).digest()

        try:
            coinbase_flag = True

            for vin in vins:
                spendable_txid = vin['txid']
                vout = int.from_bytes(vin['vout'], 'little')
                coinbase_flag = False
                spent_utxo.append(self.__spend_utxo(spendable_txid, vout, spending_txid))

            vouts = self.blockchain.get_vouts(tx_info)
            
            for i, vout in enumerate(vouts):
                key = self.__create_key(hashlib.sha256(tx_info).digest(), i)
                
                tx_utxo = self.__create_utxo_struct(vout, coinbase_flag)

                self.db.put(key, tx_utxo)
            
        except Exception:
            raise

    def __create_utxo_struct(self, vout: dict, coinbase_flag: bool):
        res = int(coinbase_flag).to_bytes(self.UTXO_STRUCT['coinbase'], 'little')
        res += self.blockchain.get_chain_len().to_bytes(self.UTXO_STRUCT['height'], 'little')
        res += (0).to_bytes(self.UTXO_STRUCT['spent'], 'little')
        res += (0).to_bytes(self.UTXO_STRUCT['spent_by'], 'little')
        
        res += vout['value']
        res += vout['script_pub_key_size']
        res += vout['script_pub_key']

        return res

    def __get_key_property_offset(self, property_name: str):
        return self.__get_property_offset(self.KEY_STRUCT, property_name)

    def __get_utxo_property_offset(self, property_name: str):
        return self.__get_property_offset(self.UTXO_STRUCT, property_name)

    def __get_property_offset(self, dictionary: dict, property_name: str):
        cur_offset = 0

        for key, value in dictionary.items():
            if key == property_name:
                return cur_offset
            
            else:
                cur_offset += value

        raise ValueError('No such key in dictionary')
            
    def __create_key(self, txid: bytes, vout: int):
        byte_len = self.__count_byte_length(vout)
        return self.TX_LETTER.encode() + txid + byte_len.to_bytes(self.KEY_STRUCT['index_len'], 'little') + vout.to_bytes(byte_len, 'little')

    def __parse_utxo_data(self, utxo_data: bytes):
        cur_offset = 0
        utxo = {}
        utxo['coinbase'] = bool(int.from_bytes(utxo_data[cur_offset:cur_offset + self.UTXO_STRUCT['coinbase']], 'little'))
        cur_offset += self.UTXO_STRUCT['coinbase']
        utxo['height'] = int.from_bytes(utxo_data[cur_offset:cur_offset + self.UTXO_STRUCT['height']], 'little')
        cur_offset += self.UTXO_STRUCT['height']
        utxo['spent'] = bool(int.from_bytes(utxo_data[cur_offset:cur_offset + self.UTXO_STRUCT['spent']], 'little'))
        cur_offset += self.UTXO_STRUCT['spent']
        utxo['spent_by'] = utxo_data[cur_offset:cur_offset + self.UTXO_STRUCT['spent_by']].hex()
        cur_offset += self.UTXO_STRUCT['spent_by']
        utxo['value'] = int.from_bytes(utxo_data[cur_offset:cur_offset + self.UTXO_STRUCT['value']], 'little')
        cur_offset += self.UTXO_STRUCT['value']
        utxo['script_pub_key_size'] = int.from_bytes(utxo_data[cur_offset:cur_offset + self.UTXO_STRUCT['script_pub_key_size']], 'little')
        cur_offset += self.UTXO_STRUCT['script_pub_key_size']
        utxo['script_pub_key'] = utxo_data[cur_offset:cur_offset + utxo['script_pub_key_size']].hex()
        cur_offset += utxo['script_pub_key_size']

        return utxo
    
    def __parse_utxo_data_digest(self, utxo_data: bytes):
        cur_offset = 0
        utxo = {}
        utxo['coinbase'] = utxo_data[cur_offset:cur_offset + self.UTXO_STRUCT['coinbase']]
        cur_offset += self.UTXO_STRUCT['coinbase']
        utxo['height'] = utxo_data[cur_offset:cur_offset + self.UTXO_STRUCT['height']]
        cur_offset += self.UTXO_STRUCT['height']
        utxo['spent'] = utxo_data[cur_offset:cur_offset + self.UTXO_STRUCT['spent']]
        cur_offset += self.UTXO_STRUCT['spent']
        utxo['spent_by'] = utxo_data[cur_offset:cur_offset + self.UTXO_STRUCT['spent_by']]
        cur_offset += self.UTXO_STRUCT['spent_by']
        utxo['value'] = utxo_data[cur_offset:cur_offset + self.UTXO_STRUCT['value']]
        cur_offset += self.UTXO_STRUCT['value']
        utxo['script_pub_key_size'] = utxo_data[cur_offset:cur_offset + self.UTXO_STRUCT['script_pub_key_size']]
        cur_offset += self.UTXO_STRUCT['script_pub_key_size']
        utxo['script_pub_key'] = utxo_data[cur_offset:cur_offset + int.from_bytes(utxo['script_pub_key_size'], 'little')]
        cur_offset += int.from_bytes(utxo['script_pub_key_size'], 'little')

        return utxo
    
    def get_utxo_formatted(self, txid: bytes): return self.__parse_utxo_data(self.db.get(txid))

    def get_utxos(self):
        arr = []

        for key, value in self.db:
            txid_offset = self.__get_key_property_offset('hash_len')
            txid = key[txid_offset:self.KEY_STRUCT['hash_len'] + txid_offset].hex()
            
            cur_offset = self.__get_key_property_offset('index_len')
            vout_len = int.from_bytes(key[cur_offset:cur_offset + self.KEY_STRUCT['index_len']], 'little')
            cur_offset += self.KEY_STRUCT['index_len']
            vout = int.from_bytes(key[cur_offset:cur_offset + vout_len], 'little')
            
            utxo_value = {}
            utxo_value['txid'] = txid
            utxo_value['vout'] = vout
            utxo_value.update(self.__parse_utxo_data(value))

            arr.append(utxo_value)

        return arr

    def get_info_of_utxo_digest(self, txid: bytes, vout: int):
        key = self.__create_key(txid, vout)
        utxo_data = self.db.get(key)
        
        if not utxo_data:
            raise ValueError('[ERROR] No such vout in the chain!!!')
        
        return self.__parse_utxo_data_digest(utxo_data)

    def get_info_of_vout(self, txid: bytes, vout: int):
        key = self.__create_key(txid, vout)
        utxo_data = self.db.get(key)
        
        if not utxo_data:
            raise ValueError('[ERROR] No such vout in the chain!!!')
        
        return self.__parse_utxo_data(utxo_data)
