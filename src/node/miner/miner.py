from ...blockchain import Transaction
from ...block import Block
from ...blockchain import Blockchain

import random
import hashlib
import math

class Miner:
    def __init__(self, blockchain, pk: bytes) -> None:
        self.pk = pk
        self.blockchain = blockchain

    def mine_block(self):
        emission = Transaction([(self.pk, math.ceil(random.random() * 1000))]).tx_data
        nonce = 1
        check_proof = False
        num_of_zeros = 1
        difficulty = ''.zfill(num_of_zeros)
        prev_block_hash = self.blockchain.hash_last_block_in_digest()

        while not check_proof:
            transactions = self.blockchain.mempool.get_mempool()
            transactions.insert(0, emission)

            check_block = Block(nonce, prev_block_hash, num_of_zeros, transactions)
            block_data = check_block.create_block()

            header = check_block.header.header
            
            if hashlib.sha256(header).hexdigest()[:num_of_zeros] == difficulty:
                check_proof = True

                self.blockchain.append_block(block_data, transactions)
                # self.db.deleteTxids()

                return block_data

            else:
                nonce += 1
        
        return 1