from core.blockchain.transactions.mrkl_tree import MerkleTree
from core.blockchain.constants import *

import time

class Block:
    def __init__(self, nonce, prev_hash, difficulty, txs) -> None:
        self.nonce = nonce
        self.prev_hash = prev_hash
        self.difficulty = difficulty
        self.txs = txs
        
    def create_block(self):
        res = self.prev_hash
    
        if self.txs:
            res += MerkleTree(self.txs).root
        else:
            res += (0).to_bytes(BLOCK_STRUCT['mrkl_root'], byteorder='little')

        res += int(time.time()).to_bytes(BLOCK_STRUCT['time'], byteorder='little')
        res += self.difficulty.to_bytes(BLOCK_STRUCT['difficulty'], byteorder='little')
        res += self.nonce.to_bytes(BLOCK_STRUCT['nonce'], byteorder='little')

        self.header = res

        res += len(self.txs).to_bytes(self.TXS_STRUCT['tx_count'], byteorder='big')
        for tx in self.txs:
            res += tx

        return res
