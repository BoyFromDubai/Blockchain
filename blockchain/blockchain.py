import datetime
import hashlib
import random
import math
from blockchain.save_data import data
from blockchain.mrkl_tree import MerkleTree
import pickle
import os
import time
import ecdsa

NUMS_NUM = 4

blk_structure = [
    4, # size
    36, # prev_blk_hash
    68, # mrkl_root
    72, # time
    76, # difficulty
    80, # nonce
    81, # 
    85, # 
    86, # 
    118, # 
    122, # 
    # # 
    # # 
    123, # 
    131, # 
    135, # 
    139 # 
]

block_structure = {
    'size': 4,
    'prev_blk_hash': 32, # header info
    'mrkl_root': 32, # header info
    'time': 4, # header info
    'difficulty': 4, # header info
    'nonce': 4, # header info
    'tx_count': 1,
    'version': 4, #tx info
    'input_count': 1, #tx info
    'txid': 32, #tx info
    'vout': 4, #tx info
    'script_sig_size': None, #tx info
    'script_sig': None, #tx info
    'output_count': 1, #tx info
    'value': 8, #tx info
    'script_pub_key_size': None, #tx info
    'script_pub_key': None, #tx info
    'locktime': 4, #tx info
    
}

class Blockchain:
    def __init__(self):
        if not self.getChainLen():
            self.genezis_block = self.__append_block(self.__create_block(1, hashlib.sha256(pickle.dumps(17)).digest(), 1)) #TODO: change prev_hash

        # with open('wallet/wallet.bin', 'rb') as f:
        #     key = f.read()

        #     self.sk = ecdsa.SigningKey.from_string(key, ecdsa.SECP256k1, hashfunc=hashlib.sha256)
        self.mempool_tx_size_info = 2

    def __create_block(self, nonce, prev_hash, difficulty, transactions = []):

        res = prev_hash

        if transactions:
            res += MerkleTree(transactions).root
        else:
            res += (12).to_bytes(32, byteorder='little')

        #TODO: change this if else

        res += int(time.time()).to_bytes(block_structure['time'], byteorder='little')
        print()
        print(difficulty)
        res += difficulty.to_bytes(block_structure['difficulty'], byteorder='little')
        res += nonce.to_bytes(block_structure['nonce'], byteorder='little')
        print(res.hex())
        res += len(transactions).to_bytes(block_structure['tx_count'], byteorder='little')
        print(transactions)
        print()
        for tx in transactions:
            res += tx

        size = len(res).to_bytes(block_structure['size'], byteorder='little')

        return size + res

    def __get_mempool(self):
        transactions = []

        with open('blockchain/mempool/mempool.dat', 'rb') as f:
            all_data = f.read()

            f.seek(0)

            while f.tell() < len(all_data):
                tx_info_len = int.from_bytes(f.read(self.mempool_tx_size_info), 'little')
                transactions.append(f.read(tx_info_len))

        return transactions

    def __get_last_blk(self): return sorted(os.listdir('blockchain/blocks'))[-1]

    def __get_last_blk_txid(self):
        blk_data = self.__get_last_blk()

    def __get_last_blk_header(self):
        f = open('blockchain/blocks/' + self.__get_last_blk(), 'rb')
        
        blk_data = f.read()
        res = self.__get_blk_header(blk_data)
        f.close()

        return res

    def __get_blk_header(self, bytes):
        res = b''
        block_structure_copy = block_structure.copy()
        prev_value = block_structure_copy['size']
        del block_structure_copy['size']

        for key, size in block_structure_copy.items():
            if key == 'tx_count':
                break
            res += bytes[prev_value:prev_value + size]
            prev_value += size

        print(prev_value)
        
        return res

    def __get_prev_blk_hash(self):
        f = open('blockchain/blocks/' + self.__get_last_blk(), 'rb')
        f.seek(self.__get_offset('prev_blk_hash'))
        prev_hash = f.read(block_structure['prev_blk_hash'])
        f.close()
        
        return prev_hash
    
    def __get_offset(self, name, offset = 0, cur_dict = block_structure):
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

    def __get_property_size(self, name, cur_dict = block_structure):
        for key, value in cur_dict.items():
            if isinstance(value, dict):
                self.__get_property_size(name, value)
                
                return value
            else:
                if key == name:
                    return value

        return value
    
    def __append_block(self, bytes):
        file = f"blockchain/blocks/blk_{str(self.getChainLen() + 1).zfill(NUMS_NUM)}.dat"
        f = open(file, 'wb')
        f.write(bytes)
        f.close()
    
    def getChainLen(self): 
        if not os.path.isdir('blockchain/blocks'): 
            os.mkdir('blockchain/blocks')
            return 0
        else:
            return len(os.listdir('blockchain/blocks')) 

    def mine_block(self, pk):
        emission = self.add_transaction([math.ceil(random.random() * 100)], [pk], sk=None)
        transactions = [emission]
        mempool = self.__get_mempool()[1:]

        for tx in mempool: 
            transactions.append(tx)

        nonce = 1
        check_proof = False
        num_of_zeros = 1
        difficulty = ''.zfill(num_of_zeros)

        # for i in range(num_of_zeros):
        #     difficulty += '0'.
            
        prev_block_hash = self.__get_prev_blk_hash()
        
        while (not(check_proof)):

            check_block = self.__create_block(nonce, hashlib.sha256(prev_block_hash).digest(), num_of_zeros, transactions)
            header = self.__get_blk_header(check_block)
            
            if self.__hash_hex(header)[:num_of_zeros] == difficulty:
                print(difficulty)
                print(header.hex()) 
                check_proof = True
                self.__append_block(check_block)
                self.__clear_mempool()

                # db = plyvel.DB('chainstate/', create_if_missing=True)
                # info_for_db = []
                
                # #TODO allow adding transaction into leveldb 
                # # for i in range(self.__get_tx_number(check_block)):
                # #     vout_n_arr = []
                # #     print(self.__get_tx_number(check_block))

                # #     if check_block['transactions'][i]:
                # #         for vout in check_block['transactions'][i]['vout']:
                # #             vout_n_arr.append(vout['n'])
                # #             info_for_db.append({
                # #                 'coinbase': True if not i else False, 
                # #                 'height': check_block['index'],
                # #                 'vout_info': {
                # #                     'vout': vout['n'],
                # #                     'spent': False,
                # #                     'scriptPubKey': vout['scriptPubKey']
                # #                 }
                # #             })

                # #     db.put(hashlib.sha256(pickle.dumps(check_block['transactions'][i])).digest(), pickle.dumps(info_for_db))
                
                # db.close()

                return check_block

            else:
                nonce += 1
        
        return 1

    #TODO change mempool from json to bytes
    def __clear_mempool(self):
        with open('blockchain/mempool/mempool.dat', 'w'): 
            pass

    def __hash_hex(self, bytes): return hashlib.sha256(bytes).hexdigest()

    def __hash_digest(self, bytes): return hashlib.sha256(bytes).digest()

    def chain_len(self): return len(data.get_chain())

    def is_chain_valid(self, chain):

        prev_block = chain[0]
        block_index = 1

        while (block_index < len(chain)):
            cur_block = chain[block_index]

            if cur_block['prev_hash'] != self.__hash_hex(prev_block):
                return False
            
            prev_block = cur_block
            block_index += 1
        
        return True

    def add_transaction(self, value, addresses, sk, txid = [], vout_num = []):

        print(sk)
        version = (0).to_bytes(block_structure['version'], "little")
        tx_data = version
        inputs_num = len(txid).to_bytes(block_structure['input_count'], "little")
        tx_data += inputs_num
        
        for i in range(len(txid)):
            tx_data += self.__create_vin(txid[i], int(vout_num[i]), sk)

        tx_data += len(addresses).to_bytes(1, "big") #outputs num

        for i in range(len(addresses)):
            tx_data += self.__create_vout(int(value[i]), addresses[i])
        
        # bytes.fromhex(txid[i] if not len(txid[i]) % 2 else '0' + txid[i])

        self.__append_to_mempool(tx_data)

        return tx_data

    def __append_to_mempool(self, tx_bytes):
        if not os.path.isdir('blockchain/mempool'): 
            os.mkdir('blockchain/mempool')
        
        with open('blockchain/mempool/mempool.dat', 'ab') as f:
            f.write(len(tx_bytes).to_bytes(self.mempool_tx_size_info, 'little'))
            f.write(tx_bytes)

        # with open('blockchain/mempool/mempool.dat', 'wb') as f:
        #     pass
            
    def get_chain(self): return data.get_chain()

    def __create_vin(self, txid, vout_num, sk):
        if not txid or not vout_num:
            return None

        vin_data = int(txid, 16).to_bytes(block_structure['txid'], 'little')
        vin_data += vout_num.to_bytes(block_structure['vout'], "little")

        # TODO: change scriptSig
        vin_data += (1).to_bytes(1, "big") #ScriptSig size
        vin_data += (100).to_bytes(1, "big") #ScriptSig

        return vin_data

    def __create_vout(self, value, address):

        vout_data = int(value).to_bytes(block_structure['value'], "little")
        # TODO: change scriptPubKey
        len_of_script_pub_key = math.ceil(len(address) / 2)
        vout_data += len_of_script_pub_key.to_bytes(1, "big") #ScriptPubKey size
        vout_data += int(address, 16).to_bytes(len_of_script_pub_key, 'big')#ScriptPubKey

        return vout_data