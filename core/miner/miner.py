from core.blockchain.block import Block
import math
import random
import hashlib


class Miner():
    def __init__(self, blockchain) -> None:
        self.blockchain = blockchain
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
            block_data = check_block.createBlock()

            header = check_block.header.header
            
            if hashlib.sha256(header).hexdigest()[:num_of_zeros] == difficulty:
                check_proof = True

                for tx in transactions:
                    self.appendVoutsToDb(tx)

                return block_data

            else:
                nonce += 1
        
        return 1