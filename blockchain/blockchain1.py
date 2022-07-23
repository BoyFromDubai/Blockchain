import datetime
import hashlib
import json
import requests
from urllib.parse import urlparse
import random
import math

from blockchain.mrkl_tree import MerkleTree

class Blockchain:
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.append_block(self.create_block(1, '0', '00'))

    def create_block(self, nonce, prev_hash, difficulty):
        block = {
            'index': len(self.chain) + 1,
            'header': {
                'timestamp': str(datetime.datetime.now()),
                'prev_hash': prev_hash,
                'mrkl_root': MerkleTree(self.transactions).root,
                'nonce': nonce,
                'difficulty': difficulty
            },
            'transaction_counter': len(self.transactions),
            'transactions': self.transactions
        }

        return block

    def append_block(self, block):
        self.chain.append(block)

    def get_prev_block(self):
        return self.chain[len(self.chain) - 1]

    def mine_block(self, pk):
        self.add_transaction([math.ceil(random.random() * 100)], [pk])

        nonce = 1
        check_proof = False
        difficulty = '00'
        
        while (not(check_proof)):

            check_block = self.create_block(nonce, self.hash(self.get_prev_block()), difficulty)
            
            if (str(self.hash(check_block))[:2] == difficulty): 
                check_proof = True
                self.append_block(check_block)
                self.transactions = []

                return check_block

            else:
                nonce += 1
        
        return 1

    def hash(self, block):
        # encoded_block = json.dumps(block, sort_keys = True).encode()
        encoded_block_header = str(block['header']).encode()
        return hashlib.sha256(encoded_block_header).hexdigest()

    def chain_len(self):
        return len(self.chain)

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
            'locktime': 0,
            'vin': vin,
            'vout': vout
        }

        self.transactions.append(transaction)

        return transaction

    def get_chain(self):
        return self.chain

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
            'scriptPubSig': {
                'asm': None,
                'hex': None,
                'reqSigs': None,
                'addresses': addresses,
            }
        }    

        return vout

    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_len = len(self.chain)

        for node in network:
            response = requests.get(f'http://{node}/full_chain')
            
            if response.status_code == 200:
                cur_len = response.json()['length']
                cur_chain = response.json()['chain']

                if (cur_len > max_len and self.is_chain_valid(cur_chain)):
                    max_len = cur_len
                    longest_chain = cur_chain
        
        if longest_chain:
            self.chain = longest_chain
            return True
        else:
            return False