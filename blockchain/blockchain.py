import datetime
import hashlib
import random
import math
from blockchain.save_data import data
from blockchain.mrkl_tree import MerkleTree
import pickle
import plyvel
import os
import time

NUMS_NUM = 4



class Blockchain:
    def __init__(self):
        if not self.__get_chain_length():
            self.genezis_block = self.__append_block(self.__create_block(1, hashlib.sha256(pickle.dumps(17)).digest(), 1)) #TODO: change prev_hash

    def __create_block(self, nonce, prev_hash, difficulty, transactions = []):
        length = self.chain_len()

        res = prev_hash

        if (transactions):
            res += MerkleTree(transactions).root
        else:
            res += (12).to_bytes(32, byteorder='little')

        #TODO: change this if else

        res += int(time.time()).to_bytes(data.block_structure['header']['time'], byteorder='little')
        res += difficulty.to_bytes(data.block_structure['header']['difficulty'], byteorder='little')
        res += nonce.to_bytes(data.block_structure['header']['nonce'], byteorder='little')
        res += len(transactions).to_bytes(data.block_structure['tx_count'], byteorder='little')

        for tx in transactions:
            res += tx['version'].to_bytes(data.block_structure['tx_data']['version'], byteorder='little')
            res += len(tx['vin']).to_bytes(data.block_structure['tx_data']['input_count'], byteorder='little')
            
            for vin in tx['vin']:
                res += bytes.fromhex(vin['txid'])
                res += int(vin['vout']).to_bytes(data.block_structure['tx_data']['input']['vout'], byteorder='little')
                # scriptSig size
                # scriptSig
            
            res += len(tx['vout']).to_bytes(data.block_structure['tx_data']['output_count'], byteorder='little')

            for vout in tx['vout']:
                res += int(vout['value']).to_bytes(data.block_structure['tx_data']['output']['value'], byteorder='little')
                # scriptPubKey size
                # scriptPubKey

            res += tx['locktime'].to_bytes(data.block_structure['tx_data']['locktime'], byteorder='little')

        size = len(res).to_bytes(data.block_structure['size'], byteorder='little')

        return size + res

    def __get_mempool(self): return data.get_mempool()

    def __get_last_blk_header(self):
        f = open('blockchain/blocks/' + self.__get_last_block(), 'rb')
        
        blk_data = f.read()
        res = self.__get_blk_header(blk_data)
        f.close()
        print(res)
        return res

    def __get_blk_header(self, bytes):
        res = b''
        prev_value = data.block_structure['size']
        for key, value in data.block_structure['header'].items():
            res += bytes[prev_value:prev_value + value]
            prev_value += value

        print(res)
        
        return res

    def __get_prev_blk_hash(self):
        f = open('blockchain/blocks/' + self.__get_last_block(), 'rb')
        f.seek(self.__get_offset('prev_blk_hash'))
        prev_hash = f.read(data.block_structure['header']['prev_blk_hash'])
        f.close()
        
        return prev_hash
    
    def __get_offset(self, name, offset = 0, cur_dict = data.block_structure):
        cur_offset = offset

        for key, value in cur_dict.items():
            if isinstance(value, dict):
                cur_offset = self.__get_offset(name, cur_offset, value)
                
                return cur_offset
            else:
                if key != name:
                    cur_offset += value
                else: 
                    return cur_offset
        
        return cur_offset

    def __get_property_size(self, name, cur_dict = data.block_structure):
        for key, value in cur_dict.items():
            if isinstance(value, dict):
                self.__get_property_size(name, value)
                
                return value
            else:
                if key == name:
                    return value

        return value

    def get_property(self, bytes, name):
        offset = self.__get_offset(name)
        size = self.__get_property_size(name)

        return bytes[offset:offset + size]

    def __get_tx_number(self, bytes): return int.from_bytes(bytes[self.__get_offset('tx_count'):self.__get_offset('tx_count') + data.block_structure['tx_count']], 'little')
        
    def __append_block(self, bytes):
        file = f"blockchain/blocks/blk_{str(self.__get_chain_length() + 1).zfill(NUMS_NUM)}.dat"
        f = open(file, 'wb')
        f.write(bytes)
        f.close()
    
    def __get_chain_length(self): return len(os.listdir('blockchain/blocks'))

    def __get_last_block(self): return sorted(os.listdir('blockchain/blocks'))[-1]

    def mine_block(self, pk):
        emission = self.add_transaction([math.ceil(random.random() * 100)], [pk])
        transactions = [emission]
        mempool = self.__get_mempool()

        for tx in mempool: 
            transactions.append(tx)

        nonce = 1
        check_proof = False
        num_of_zeros = 1
        difficulty = ''

        for i in range(num_of_zeros):
            difficulty += '0'
            
        prev_block_hash = self.__get_prev_blk_hash()
        
        while (not(check_proof)):

            check_block = self.__create_block(nonce, hashlib.sha256(prev_block_hash).digest(), num_of_zeros, transactions)
            header = self.__get_blk_header(check_block)
            print(header)
            
            if (self.hash_hex(header)[:1] == difficulty): 
                check_proof = True
                self.__append_block(check_block)
                self.__clear_mempool()

                db = plyvel.DB('chainstate/', create_if_missing=True)
                info_for_db = []
                
                #TODO allow adding transaction into leveldb 
                # for i in range(self.__get_tx_number(check_block)):
                #     vout_n_arr = []
                #     print(self.__get_tx_number(check_block))

                #     if check_block['transactions'][i]:
                #         for vout in check_block['transactions'][i]['vout']:
                #             vout_n_arr.append(vout['n'])
                #             info_for_db.append({
                #                 'coinbase': True if not i else False, 
                #                 'height': check_block['index'],
                #                 'vout_info': {
                #                     'vout': vout['n'],
                #                     'spent': False,
                #                     'scriptPubKey': vout['scriptPubKey']
                #                 }
                #             })

                #     db.put(hashlib.sha256(pickle.dumps(check_block['transactions'][i])).digest(), pickle.dumps(info_for_db))
                
                db.close()

                return check_block

            else:
                nonce += 1
        
        return 1

    #TODO change mempool from json to bytes
    def __clear_mempool(self):
        file = "blockchain/mempool/mempool.json"
        f = open(file, 'r+')
        f.truncate(0)
        f.close()

    def hash_hex(self, bytes): return hashlib.sha256(bytes).hexdigest()

    def hash_digest(self, bytes): return hashlib.sha256(bytes).digest()

    def chain_len(self): return len(data.get_chain())

    def is_chain_valid(self, chain):
        prev_block = chain[0]
        block_index = 1

        while (block_index < len(chain)):
            cur_block = chain[block_index]

            if cur_block['header']['prev_hash'] != self.hash_hex(prev_block):
                return False
            
            prev_block = cur_block
            block_index += 1
        
        return True

    def add_transaction(self, value, addresses, txid = [], vout_num = []):
        vout = []
        vin = []

        for i in range(len(addresses)):
            vout.append(self.__create_vout(int(value[i]), i, addresses[i]))
        for i in range(len(txid)):
            vin.append(self.__create_vin(bytes.fromhex(hex(int(txid[i], 16))), int(vout_num[i])))
        
        transaction = {
            'version': 0,
            'vin': vin,
            'vout': vout,
            'locktime': 0,
        }

        return transaction

    def get_chain(self): return data.get_chain()

    def __create_vin(self, txid, vout_num):
        if not txid or not vout_num:
            return None

        vin = {
            'txid': txid,
            'vout': vout_num,
            'scriptSig': {
                'asm': None,
                'hex': None
            },
            'sequence': None
        }

        return vin

    def __create_vout(self, value, n, addresses):
        vout = {
            'value': value,
            'n': n,
            'scriptPubKey': {
                'asm': None,
                'hex': None,
                'reqSigs': None,
                'addresses': addresses,
            }
        }    

        return vout