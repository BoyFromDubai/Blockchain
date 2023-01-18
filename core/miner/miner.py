from core.blockchain.block import Block
from core.database.db import DB
import math
import random
import hashlib


class Miner():
    def __init__(self, blockchain, db) -> None:
        self.blockchain = blockchain
        self.db = db
    # def __init__(self, get_mempool, hash_last_blk_hash_digest) -> None:
    #     self.get_mempool_callback = get_mempool
    #     self.hash_last_blk_hash_digest_callback = hash_last_blk_hash_digest

    def mine_block(self, pk):
        emission = self.blockchain.create_transaction([(pk, math.ceil(random.random() * 1000))])
        nonce = 1
        check_proof = False
        num_of_zeros = 1
        difficulty = ''.zfill(num_of_zeros)
        prev_block_hash = self.blockchain.hash_last_block_in_digest()

        while not check_proof:
            transactions = self.blockchain.get_mempool()
            transactions.insert(0, emission)

            check_block = Block(nonce, prev_block_hash, num_of_zeros, transactions)
            block_data = check_block.create_block()

            header = check_block.header
            
            if hashlib.sha256(header).hexdigest()[:num_of_zeros] == difficulty:
                check_proof = True

                for tx in transactions:
                    cur_height = self.blockchain.get_chain_len()
                    cur_txid = hashlib.sha256(tx).digest()
                    vins = self.blockchain.parse_vins(tx)
                    vouts = self.blockchain.parse_vouts(tx)
                    self.db.add_tx_to_db(cur_height, cur_txid, vins, vouts)

                return block_data

            else:
                nonce += 1
        
        return 1