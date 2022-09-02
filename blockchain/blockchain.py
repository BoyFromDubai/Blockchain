import datetime
import hashlib
import random
import math
from sys import byteorder
from blockchain.save_data import data
from blockchain.mrkl_tree import MerkleTree
import pickle
import plyvel
import time

block_structure = {
    'size': 4,
    'header': {
        'prev_blk_hash': 32,
        'mrkl_root': 32,
        'time': 4,
        'difficulty': 4,
        'nonce': 4
    },
    'tx_count': 1,
    'tx_data': {
        'version': 4,
        'input_count': 1,
        'input': {
            'txid': 32,
            'vout': 4,
            'script_sig_size': None,
            'script_sig': None,
        },
        'output_count': 1,
        'output': {
            'value': 8,
            'script_pub_key_size': None,
            'script_pub_key': None
        },
        'locktime': 4,
    }
}

class Blockchain:
    def __init__(self):
        if not self.get_chain():
            self.genezis_block = self.append_block(self.__create_block(1, hex(17), '00'))

    def __create_block(self, nonce, prev_hash, difficulty, transactions = []):
        length = self.chain_len()

        file = f"baa.dat"
        f = open(file, 'wb')

        res = bytes.fromhex(prev_hash)
        res += bytes.fromhex(MerkleTree(transactions).root)
        res += int(time.time()).to_bytes(block_structure['header']['time'], byteorder='little')
        res += difficulty.to_bytes(block_structure['header']['difficulty'], byteorder='little')
        res += nonce.to_bytes(block_structure['header']['nonce'], byteorder='little')
        res += len(transactions).to_bytes(block_structure['tx_count'], byteorder='little')

        for tx in transactions:
            res += tx['version'].to_bytes(block_structure['tx_data']['version'], byteorder='little')
            res += len(tx['vin']).to_bytes(block_structure['tx_data']['input_count'], byteorder='little')
            print(len(tx['vin']))
            
            for vin in tx['vin']:
                res += bytes.fromhex(vin['txid'])
                res += int(vin['vout']).to_bytes(block_structure['tx_data']['input']['vout'], byteorder='little')
                # scriptSig size
                # scriptSig
                res += int(vin['vout']).to_bytes(block_structure['tx_data']['input']['vout'], byteorder='little')
            
            res += len(tx['vout']).to_bytes(block_structure['tx_data']['output_count'], byteorder='little')

            for vout in tx['vout']:
                res += int(vout['value']).to_bytes(block_structure['tx_data']['output']['value'], byteorder='little')
                # scriptPubKey size
                # scriptPubKey

            res += tx['locktime'].to_bytes(block_structure['tx_data']['locktime'], byteorder='little')

        print(res.hex())
        f.write(res)
        f.close()

        block = {
            'index': length + 1,
            'header': {
                'prev_hash': prev_hash,
                'mrkl_root': MerkleTree(transactions).root,
                'timestamp': int(time.time()),
                'difficulty': difficulty,
                'nonce': nonce,
            },
            'transaction_counter': len(transactions),
            'transactions': transactions
        }

        return block

    def __get_mempool(self):
        return data.get_mempool()

    def append_block(self, block):
        data.save_block(block)

    def get_prev_block(self):
        return data.get_last_block()

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
        prev_block = self.get_prev_block()
        
        while (not(check_proof)):

            check_block = self.__create_block(nonce, self.hash(prev_block), num_of_zeros, transactions)
            
            if (str(self.hash(check_block))[:1] == difficulty): 
                check_proof = True
                self.append_block(check_block)
                self.__clear_mempool()

                db = plyvel.DB('chainstate/', create_if_missing=True)
                info_for_db = []

                for i in range(len(check_block['transactions'])):
                    vout_n_arr = []

                    if check_block['transactions'][i]:
                        for vout in check_block['transactions'][i]['vout']:
                            vout_n_arr.append(vout['n'])
                            info_for_db.append({
                                'coinbase': True if not i else False, 
                                'height': check_block['index'],
                                'vout_info': {
                                    'vout': vout['n'],
                                    'spent': False,
                                    'scriptPubKey': vout['scriptPubKey']
                                }
                            })

                    db.put(hashlib.sha256(pickle.dumps(check_block['transactions'][i])).digest(), pickle.dumps(info_for_db))
                
                db.close()

                return check_block

            else:
                nonce += 1
        
        return 1

    def __clear_mempool(self):
        data.clear_mempool()

    def hash(self, block):
        return hashlib.sha256(pickle.dumps(block['header'])).hexdigest()

    def chain_len(self):
        return len(data.get_chain())

    def is_chain_valid(self, chain):
        prev_block = chain[0]
        block_index = 1

        while (block_index < len(chain)):
            cur_block = chain[block_index]

            if cur_block['header']['prev_hash'] != self.hash(prev_block):
                return False
            
            prev_block = cur_block
            block_index += 1
        
        return True

    def add_transaction(self, value, addresses, txid = [], vout_num = []):
        vout = []
        vin = []

        for i in range(len(addresses)):
            vout.append(self.__create_vout(value[i], i, addresses[i]))
        for i in range(len(txid)):
            vin.append(self.__create_vin(txid[i], vout_num[i]))
        
        transaction = {
            'version': 0,
            'vin': vin,
            'vout': vout,
            'locktime': 0,
        }

        return transaction

    def get_chain(self):
        return data.get_chain()

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