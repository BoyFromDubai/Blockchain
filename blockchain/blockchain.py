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
from blocks_parser.parser import *
from blockchain.blk_structure import *

# blk_structure = [
#     4, # size
#     36, # prev_blk_hash
#     68, # mrkl_root
#     72, # time
#     76, # difficulty
#     80, # nonce
#     81, # 
#     85, # 
#     86, # 
#     118, # 
#     122, # 
#     # # 
#     # # 
#     123, # 
#     131, # 
#     135, # 
#     139 # 
# ]

class Blockchain:
    def __init__(self):
        if not getBlockchainLen():
            self.genezis_block = self.__append_block(self.__create_block(1, hashlib.sha256(pickle.dumps(17)).digest(), 1)) #TODO: change prev_hash

        self.mempool_tx_size_info = 2

    def __create_block(self, nonce, prev_hash, difficulty, transactions = []):

        res = prev_hash

        if transactions:
            res += MerkleTree(transactions).root
        else:
            res += (0).to_bytes(block_structure['mrkl_root'], byteorder='little')


        res += int(time.time()).to_bytes(block_structure['time'], byteorder='little')
        res += difficulty.to_bytes(block_structure['difficulty'], byteorder='little')
        res += nonce.to_bytes(block_structure['nonce'], byteorder='little')
        res += len(transactions).to_bytes(block_structure['tx_count'], byteorder='little')
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
    
    def __append_block(self, blk):
        file = f"blockchain/blocks/blk_{str(getBlockchainLen() + 1).zfill(NUMS_NUM)}.dat"
        f = open(file, 'wb')
        f.write(blk)
        f.close()

    def mine_block(self, pk):
        emission = self.add_transaction([math.ceil(random.random() * 100)], [pk], sk=None, isTransaction=False)
        transactions = [emission]
        # mempool = self.__get_mempool()[1:]
        mempool = self.__get_mempool()

        for tx in mempool: 
            transactions.append(tx)

        nonce = 1
        check_proof = False
        num_of_zeros = 1
        difficulty = ''.zfill(num_of_zeros)
            
        prev_block_hash = hashLastBlockInDigest()
        
        while (not(check_proof)):

            check_block = self.__create_block(nonce, prev_block_hash, num_of_zeros, transactions)
            header = getBlockHeader(check_block)
            
            if hashInHex(header)[:num_of_zeros] == difficulty:
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

    def verifyChain(self):
        block_files = getBlockFiles()
        prev_blk_hash = hashNthBlockInDigest(0)
        
        if len(block_files) > 1:
            for i in range(1, len(block_files)):
                cur_blk_prev_hash = getNthBlockPrevHash(i)

                if prev_blk_hash != cur_blk_prev_hash:
                    return False
                else:
                    prev_blk_hash = hashNthBlockInDigest(i)
            
            return True

    def add_transaction(self, value, addresses, sk, txid = [], vout_num = [], isTransaction = True):

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
        if isTransaction:
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
        scriptSig = (100).to_bytes(1, "big")
        vin_data += (1).to_bytes(1, "big") #ScriptSig size
        vin_data += scriptSig #ScriptSig

        return vin_data

    def __create_vout(self, value, address):

        vout_data = int(value).to_bytes(block_structure['value'], "little")

        # TODO: change scriptPubKey
        len_of_script_pub_key = math.ceil(len(address) / 2)
        vout_data += len_of_script_pub_key.to_bytes(1, "big") #ScriptPubKey size
        vout_data += int(address, 16).to_bytes(len_of_script_pub_key, 'big')#ScriptPubKey

        return vout_data