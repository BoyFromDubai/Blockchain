import time
from ..blockchain import BLOCK_STRUCT
from ..merkle_tree import MerkleTree

class Header:
    def __init__(self, nonce, prev_hash, difficulty, txs) -> None:
        self.nonce = nonce
        self.prev_hash = prev_hash
        self.difficulty = difficulty
        self.txs = txs

        self.header = self.create_header()

    def create_header(self) -> bytes:
    
        res = self.prev_hash
    
        if self.txs:
            res += MerkleTree(self.txs).root
        else:
            res += (0).to_bytes(BLOCK_STRUCT['mrkl_root'], byteorder='little')

        res += int(time.time()).to_bytes(BLOCK_STRUCT['time'], byteorder='little')
        res += self.difficulty.to_bytes(BLOCK_STRUCT['difficulty'], byteorder='little')
        res += self.nonce.to_bytes(BLOCK_STRUCT['nonce'], byteorder='little')

        return res

class Block:
    def __init__(self, nonce, prev_block_hash, num_of_zeros, transactions) -> None:
        self.header = Header(nonce, prev_block_hash, num_of_zeros, transactions)
        self.txs = transactions

    def create_block(self):
        return self.header.header + len(self.txs).to_bytes(BLOCK_STRUCT['tx_count'], 'little') + b''.join(self.txs)