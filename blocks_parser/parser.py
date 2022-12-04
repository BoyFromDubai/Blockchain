import os
from blockchain.blk_structure import *
import hashlib
# class BlockchainParser():

def getBlockchainLen(): return len(os.listdir('blockchain/blocks')) if os.path.exists('blockchain/blocks') else 0 

def getBlockFiles(): return sorted(os.listdir('blockchain/blocks'))

def getBlockHeader(data):
    res = b''
    block_structure_copy = block_structure.copy()
    prev_value = block_structure_copy['size']
    del block_structure_copy['size']

    for key, size in block_structure_copy.items():
        if key == 'tx_count':
            break
        res += data[prev_value:prev_value + size]
        prev_value += size

    print(prev_value)
    
    return res


def hashInHex(data): return hashlib.sha256(data).hexdigest()

def hashInDigest(data): return hashlib.sha256(data).digest()

def getNthBlock(n):
    with open(f'blockchain/blocks/blk_{str(n + 1).zfill(NUMS_NUM)}.dat', 'rb') as f:
        return f.read()

def getNthBlockHeader(n): return getBlockHeader(getNthBlock(n))

def getNthBlockPrevHash(n):
    return getNthBlockHeader(n)[:block_structure['prev_blk_hash']]

def hashNthBlockInHex(n): return hashInHex(getNthBlock(n)[block_structure['size']:])

def hashNthBlockInDigest(n): return hashInDigest(getNthBlock(n)[block_structure['size']:])

def getLastBlock(): return getNthBlock(getBlockchainLen() - 1)

def getLastBlockHeader(): return getNthBlockHeader(getBlockchainLen() - 1)

def getLastBlockHash(): return getNthBlockPrevHash(getBlockchainLen() - 1)

def hashLastBlockInHex(): return hashNthBlockInHex(getBlockchainLen() - 1)

def hashLastBlockInDigest(): return hashNthBlockInDigest(getBlockchainLen() - 1)



