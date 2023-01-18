from core.blockchain.constants import *

import plyvel
import os

class DB():
    VOUTS_STRUCT = {
        'height':               4,
        'vouts_num':            1,
        'spent':                32, 
        'value':                8, 
        'script_pub_key_size':  8,
        'script_pub_key':       None, 
    }

    TXID_LEN = 32
    VOUT_SIZE = 4
    TTL_OF_SPENT_TX = 5

    def __init__(self):
        self.db = plyvel.DB('chainstate/', create_if_missing=True)
        self.tmp_db = plyvel.DB('tmp_db/', create_if_missing=True)

        if not os.path.exists('blockchain/txids_to_delete'):
            os.mkdir('blockchain/txids_to_delete')

    def __del__(self):
        self.db.close()

    def __create_utxo_struct(self, cur_height, vouts):

        res = cur_height.to_bytes(DB.VOUTS_STRUCT['height'], 'little')
        res += len(vouts).to_bytes(DB.VOUTS_STRUCT['vouts_num'], 'little')
        
        for i in range(len(vouts)):
            res += (0).to_bytes(DB.VOUTS_STRUCT['spent'], 'little')
            res += vouts[i]['value']
            res += vouts[i]['script_pub_key_size']
            res += vouts[i]['script_pub_key']

        return res
    
    def showDB(self):
        arr = []
        for key, value in self.db:
            arr.append((key.hex(), self.__parse_tx_utxos(value)))

        return arr

    def showDBDigest(self):
        arr = []
        for key, value in self.db:
            arr.append((key, self.__parse_tx_utxos(value)))

        return arr

    def showTmpDB(self):
        arr = []
        for key, value in self.tmp_db:
            arr.append((key.hex(), self.__parse_tx_utxos(value)))

        return arr

    def __parse_tx_utxos(self, tx_utxos_digest):
        cur_offset = 0
        utxos_dict = {}
        utxos_dict['hight'] = int.from_bytes(tx_utxos_digest[cur_offset:cur_offset + self.VOUTS_STRUCT['height']], 'little')
        cur_offset += self.VOUTS_STRUCT['height']
        utxos_dict['vouts_num'] = int.from_bytes(tx_utxos_digest[cur_offset:cur_offset + self.VOUTS_STRUCT['vouts_num']], 'little')
        cur_offset += self.VOUTS_STRUCT['vouts_num']

        utxos = []

        for _ in range(utxos_dict['vouts_num']):
            utxo = {}

            utxo['spent'] = tx_utxos_digest[cur_offset:cur_offset + self.VOUTS_STRUCT['spent']].hex()
            cur_offset += self.VOUTS_STRUCT['spent']
            utxo['value'] = int.from_bytes(tx_utxos_digest[cur_offset:cur_offset + self.VOUTS_STRUCT['value']], 'little')
            cur_offset += self.VOUTS_STRUCT['value']
            utxo['script_pub_key_size'] = int.from_bytes(tx_utxos_digest[cur_offset:cur_offset + self.VOUTS_STRUCT['script_pub_key_size']], 'little')
            cur_offset += self.VOUTS_STRUCT['script_pub_key_size']
            utxo['script_pub_key'] = tx_utxos_digest[cur_offset:cur_offset + utxo['script_pub_key_size']].hex()
            cur_offset += utxo['script_pub_key_size']

            utxos.append(utxo)

        utxos_dict['vouts'] = utxos

        return utxos_dict

    def __change_spent_field(self, tx_utxos_digest, vout, new_txid, txid_in_vin):
        cur_offset = 0        
        res = tx_utxos_digest[cur_offset:cur_offset + self.VOUTS_STRUCT['height']]
        cur_offset += self.VOUTS_STRUCT['height']
        vouts_num = tx_utxos_digest[cur_offset:cur_offset + self.VOUTS_STRUCT['vouts_num']] 
        res += vouts_num
        cur_offset += self.VOUTS_STRUCT['vouts_num']

        delete_tx = True

        for i in range(int.from_bytes(vouts_num, 'little')):
            spent = tx_utxos_digest[cur_offset:cur_offset + self.VOUTS_STRUCT['spent']]
            cur_offset += self.VOUTS_STRUCT['spent']
            
            if i == vout:
                if not int.from_bytes(spent, 'little'):
                    print('SPENT SUCCESSFULLY')
                    res += new_txid 
                elif spent == new_txid:
                    print('NORMAL SPENT')
                else:
                    print('DOUBLE SPENDING DETECTED!!!')
                    raise ValueError('DOUBLE SPENDING DETECTED!!!')
            else:
                if not int.from_bytes(spent, 'little'):
                    delete_tx = False

                res += spent

            res += tx_utxos_digest[cur_offset:cur_offset + self.VOUTS_STRUCT['value']] 
            cur_offset += self.VOUTS_STRUCT['value']            
            pub_key_size = tx_utxos_digest[cur_offset:cur_offset + self.VOUTS_STRUCT['script_pub_key_size']] 
            res += pub_key_size
            cur_offset += self.VOUTS_STRUCT['script_pub_key_size']
            res += tx_utxos_digest[cur_offset:cur_offset + int.from_bytes(pub_key_size, 'little')]
            cur_offset += int.from_bytes(pub_key_size, 'little')

        return res, delete_tx

    def add_tx_to_db(self, cur_height, cur_txid, vins, vouts):
        vouts_to_spend = []

        for vin in vins:
            txid_in_vin = vin['txid']
            vout = int.from_bytes(vin['vout'], 'little')
            vouts_to_spend.append((txid_in_vin, self.__spend_utxo(cur_height, txid_in_vin, vout, cur_txid)))

        tx_utxos = self.__create_utxo_struct(cur_height, vouts)
        
        self.db.put(cur_txid, tx_utxos)

        return vouts_to_spend

    def __get_vout(self, utxos_info, n):
        vouts_num_offset = self.__get_property_offset('vouts_num')
        vouts_num = int.from_bytes(utxos_info[vouts_num_offset:vouts_num_offset + self.VOUTS_STRUCT['vouts_num']], 'little')
        vouts_info = utxos_info[vouts_num_offset + self.VOUTS_STRUCT['vouts_num']:]
        
        cur_offset = 0
        for i in range(vouts_num):
            res = b''
            cur_offset += self.VOUTS_STRUCT['spent']
            res += vouts_info[cur_offset:cur_offset + self.VOUTS_STRUCT['value']]
            cur_offset += self.VOUTS_STRUCT['value']
            script_pub_key_size = vouts_info[cur_offset:cur_offset + self.VOUTS_STRUCT['script_pub_key_size']] 
            res += script_pub_key_size
            cur_offset += self.VOUTS_STRUCT['script_pub_key_size']
            res += vouts_info[cur_offset:cur_offset + int.from_bytes(script_pub_key_size, 'little')]
            cur_offset += int.from_bytes(script_pub_key_size, 'little')

            if i == n:
                return res

    def __spend_utxo(self, cur_height, txid_in_vin, vout, new_txid):
        tx_utxos = self.db.get(txid_in_vin)
        vout_to_spend = self.__get_vout(tx_utxos, vout)
        updated_tx, delete_tx = self.__change_spent_field(tx_utxos, vout, new_txid, txid_in_vin)      

        if not updated_tx:
            raise ValueError('[ERROR] This vout if already spend!!!')
        else:
            self.db.delete(txid_in_vin)
            self.db.put(txid_in_vin, updated_tx)

            if delete_tx:
                with open(f'blockchain/txids_to_delete/txids_for_blk_{str(cur_height).zfill(NUM_OF_NUMBERS_IN_BLK_FILE)}.dat', 'ab') as f:
                    f.write(txid_in_vin)

        return vout_to_spend

    def showAll(self):
        for key, value in self.db:
            print(key)

    def __get_property_offset(self, property_name):
        cur_offset = 0

        for key, value in self.VOUTS_STRUCT.items():
            if key == property_name:
                return cur_offset
            else:
                cur_offset += value

        return False

    def getInfoOfTxid(self, txid):
        info_to_txid = self.db.get(txid)
        
        if not info_to_txid:
            raise ValueError('[ERROR] No such TXID in chain!!!')
        
        else:
            info_for_txid = {}
            cur_offset = 0

            info_for_txid['height'] = info_to_txid[cur_offset:cur_offset + self.VOUTS_STRUCT['height']]
            cur_offset += self.VOUTS_STRUCT['height']
            info_for_txid['vouts_num'] = info_to_txid[cur_offset:cur_offset + self.VOUTS_STRUCT['vouts_num']]
            cur_offset += self.VOUTS_STRUCT['vouts_num']

            vouts = []
            for _ in range(int.from_bytes(info_for_txid['vouts_num'], 'little')):
                vout = {}

                vout['spent'] = info_to_txid[cur_offset:cur_offset + self.VOUTS_STRUCT['spent']]
                cur_offset += self.VOUTS_STRUCT['spent']
                vout['value'] = info_to_txid[cur_offset:cur_offset + self.VOUTS_STRUCT['value']]
                cur_offset += self.VOUTS_STRUCT['value']
                
                vout['script_pub_key_size'] = info_to_txid[cur_offset:cur_offset + self.VOUTS_STRUCT['script_pub_key_size']]
                cur_offset += self.VOUTS_STRUCT['script_pub_key_size']
                vout['script_pub_key'] = info_to_txid[cur_offset:cur_offset + int.from_bytes(vout['script_pub_key_size'], 'little')]
                cur_offset += int.from_bytes(vout['script_pub_key_size'], 'little')

                vouts.append(vout)

            info_for_txid['vouts'] = vouts

            return info_for_txid
