import plyvel
import hashlib
from ..blockchain import NUMS_IN_NAME

class ChainStateDB:
    DATA_STRUCT = {
        'height':               4,
        'vouts_num':            1,
        'spent':                32, 
        'value':                8, 
        'script_pub_key_size':  8,
        'script_pub_key':       None, 
    }

    def __init__(self, blockchain) -> None:
        # self.db = leveldb.LevelDB('chainstate/')
        self.db = plyvel.DB('chainstate/', create_if_missing=True)
        self.blockchain = blockchain

    def __del__(self):
        self.db.close()

    def __change_spent_field(self, tx_utxos_digest: bytes, vout: int, new_txid: bytes):
        cur_offset = 0        
        res = tx_utxos_digest[cur_offset:cur_offset + self.DATA_STRUCT['height']]
        cur_offset += self.DATA_STRUCT['height']
        vouts_num = tx_utxos_digest[cur_offset:cur_offset + self.DATA_STRUCT['vouts_num']] 
        res += vouts_num
        cur_offset += self.DATA_STRUCT['vouts_num']

        delete_tx = True

        for i in range(int.from_bytes(vouts_num, 'little')):
            spent = tx_utxos_digest[cur_offset:cur_offset + self.DATA_STRUCT['spent']]
            cur_offset += self.DATA_STRUCT['spent']
            
            if i == vout:
                res += new_txid 
            else:
                if not int.from_bytes(spent, 'little'):
                    delete_tx = False

                res += spent

            res += tx_utxos_digest[cur_offset:cur_offset + self.DATA_STRUCT['value']] 
            cur_offset += self.DATA_STRUCT['value']            
            pub_key_size = tx_utxos_digest[cur_offset:cur_offset + self.DATA_STRUCT['script_pub_key_size']] 
            res += pub_key_size
            cur_offset += self.DATA_STRUCT['script_pub_key_size']
            res += tx_utxos_digest[cur_offset:cur_offset + int.from_bytes(pub_key_size, 'little')]
            cur_offset += int.from_bytes(pub_key_size, 'little')

        return res, delete_tx

    def __spend_utxo(self, txid_in_vin: bytes, vout: int, new_txid: bytes):
        tx_utxos = self.db.get(txid_in_vin)
        vout_to_spend = self.__get_vout(tx_utxos, vout)
        updated_tx, delete_tx = self.__change_spent_field(tx_utxos, vout, new_txid)      

        if not updated_tx:
            raise ValueError('[ERROR] This vout if already spend!!!')
        else:
            self.db.delete(txid_in_vin)
            self.db.put(txid_in_vin, updated_tx)

            # if delete_tx:
            #     with open(f'blockchain/txids_to_delete/txids_for_blk_{str(self.blockchain.get_chain_len() - 1).zfill(NUMS_IN_NAME)}.dat', 'ab') as f:
            #         f.write(txid_in_vin)

        return vout_to_spend


    def update_db(self, tx_info: bytes):
        vins = self.blockchain.get_vins(tx_info)
        vouts_to_spend = []
        txid_in_cur_block = hashlib.sha256(tx_info).digest()

        try:
            for vin in vins:
                txid_in_vin = vin['txid']
                vout = int.from_bytes(vin['vout'], 'little')
                vouts_to_spend.append((txid_in_vin, self.__spend_utxo(txid_in_vin, vout, txid_in_cur_block)))

            tx_utxos = self.__create_utxo_struct(tx_info)
            
            self.db.put(txid_in_cur_block, tx_utxos)
        
        except Exception:
            raise

    def __create_utxo_struct(self, tx_info: bytes):
        vouts = self.blockchain.get_vouts(tx_info)

        res = self.blockchain.get_chain_len().to_bytes(self.DATA_STRUCT['height'], 'little')

        res += len(vouts).to_bytes(self.DATA_STRUCT['vouts_num'], 'little')
        
        for i in range(len(vouts)):
            res += (0).to_bytes(self.DATA_STRUCT['spent'], 'little')
            res += vouts[i]['value']
            res += vouts[i]['script_pub_key_size']
            res += vouts[i]['script_pub_key']

        return res

    def __get_property_offset(self, property_name: str):
        cur_offset = 0

        for key, value in self.DATA_STRUCT.items():
            if key == property_name:
                return cur_offset
            
            else:
                cur_offset += value

        return False

    def __get_vout(self, utxos_info: bytes, n: int):
        vouts_num_offset = self.__get_property_offset('vouts_num')
        vouts_num = int.from_bytes(utxos_info[vouts_num_offset:vouts_num_offset + self.DATA_STRUCT['vouts_num']], 'little')
        vouts_info = utxos_info[vouts_num_offset + self.DATA_STRUCT['vouts_num']:]
        
        cur_offset = 0
        for i in range(vouts_num):
            res = b''
            cur_offset += self.DATA_STRUCT['spent']
            res += vouts_info[cur_offset:cur_offset + self.DATA_STRUCT['value']]
            cur_offset += self.DATA_STRUCT['value']
            script_pub_key_size = vouts_info[cur_offset:cur_offset + self.DATA_STRUCT['script_pub_key_size']] 
            res += script_pub_key_size
            cur_offset += self.DATA_STRUCT['script_pub_key_size']
            res += vouts_info[cur_offset:cur_offset + int.from_bytes(script_pub_key_size, 'little')]
            cur_offset += int.from_bytes(script_pub_key_size, 'little')

            if i == n:
                return res


    def __parse_utxo_data(self, tx_utxos_digest: bytes):
        cur_offset = 0
        utxos_dict = {}
        utxos_dict['height'] = int.from_bytes(tx_utxos_digest[cur_offset:cur_offset + self.DATA_STRUCT['height']], 'little')
        cur_offset += self.DATA_STRUCT['height']
        utxos_dict['vouts_num'] = int.from_bytes(tx_utxos_digest[cur_offset:cur_offset + self.DATA_STRUCT['vouts_num']], 'little')
        cur_offset += self.DATA_STRUCT['vouts_num']

        utxos = []

        for _ in range(utxos_dict['vouts_num']):
            utxo = {}

            utxo['spent'] = tx_utxos_digest[cur_offset:cur_offset + self.DATA_STRUCT['spent']].hex()
            cur_offset += self.DATA_STRUCT['spent']
            utxo['value'] = int.from_bytes(tx_utxos_digest[cur_offset:cur_offset + self.DATA_STRUCT['value']], 'little')
            cur_offset += self.DATA_STRUCT['value']
            utxo['script_pub_key_size'] = int.from_bytes(tx_utxos_digest[cur_offset:cur_offset + self.DATA_STRUCT['script_pub_key_size']], 'little')
            cur_offset += self.DATA_STRUCT['script_pub_key_size']
            utxo['script_pub_key'] = tx_utxos_digest[cur_offset:cur_offset + utxo['script_pub_key_size']].hex()
            cur_offset += utxo['script_pub_key_size']

            utxos.append(utxo)

        utxos_dict['vouts'] = utxos

        return utxos_dict

    def get_utxo(self, txid: bytes): return self.db.get(txid)
    
    def get_utxo_formatted(self, txid: bytes): return self.__parse_utxo_data(self.db.get(txid))

    def get_utxos(self):
        arr = []
        for key, value in self.db:
            arr.append((key.hex(), self.__parse_utxo_data(value)))

        return arr

    def get_info_of_txid(self, txid: bytes):
        info_to_txid = self.db.get(txid)
        
        if not info_to_txid:
            raise ValueError('[ERROR] No such TXID in chain!!!')
        
        info_for_txid = {}
        cur_offset = 0

        info_for_txid['height'] = info_to_txid[cur_offset:cur_offset + self.DATA_STRUCT['height']]
        cur_offset += self.DATA_STRUCT['height']
        info_for_txid['vouts_num'] = info_to_txid[cur_offset:cur_offset + self.DATA_STRUCT['vouts_num']]
        cur_offset += self.DATA_STRUCT['vouts_num']

        vouts = []
        for _ in range(int.from_bytes(info_for_txid['vouts_num'], 'little')):
            vout = {}

            vout['spent'] = info_to_txid[cur_offset:cur_offset + self.DATA_STRUCT['spent']]
            cur_offset += self.DATA_STRUCT['spent']
            vout['value'] = info_to_txid[cur_offset:cur_offset + self.DATA_STRUCT['value']]
            cur_offset += self.DATA_STRUCT['value']
            
            vout['script_pub_key_size'] = info_to_txid[cur_offset:cur_offset + self.DATA_STRUCT['script_pub_key_size']]
            cur_offset += self.DATA_STRUCT['script_pub_key_size']
            vout['script_pub_key'] = info_to_txid[cur_offset:cur_offset + int.from_bytes(vout['script_pub_key_size'], 'little')]
            cur_offset += int.from_bytes(vout['script_pub_key_size'], 'little')

            vouts.append(vout)

        info_for_txid['vouts'] = vouts

        return info_for_txid
