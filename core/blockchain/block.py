from core.blockchain.transactions.mrkl_tree import MerkleTree
from core.blockchain.constants import *

import time

class Block:
    def __init__(self, nonce, prev_hash, difficulty, txs) -> None:
        self.__nonce = nonce
        self.__prev_hash = prev_hash
        self.__difficulty = difficulty
        self.__txs = txs
        
    def create_block(self):
        res = self.__prev_hash
    
        if self.__txs:
            res += MerkleTree(self.__txs).root
        else:
            res += (0).to_bytes(BLOCK_STRUCT['mrkl_root'], byteorder='little')

        res += int(time.time()).to_bytes(BLOCK_STRUCT['time'], byteorder='little')
        res += self.__difficulty.to_bytes(BLOCK_STRUCT['difficulty'], byteorder='little')
        res += self.__nonce.to_bytes(BLOCK_STRUCT['nonce'], byteorder='little')

        self.header = res

        res += len(self.__txs).to_bytes(BLOCK_STRUCT['tx_count'], byteorder='big')
        for tx in self.__txs:
            res += tx

        return res
