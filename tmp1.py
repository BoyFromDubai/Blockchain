with open('blockchain/blocks/blk_0000.dat', 'rb') as f:
    print(f.read())

# import json
# # getNthBlockTxs(2)

# with open('tmp.json', 'w') as f:
#     json.dump(parseBlock(1), f)

# with open('blockchain/blocks/blk_0002.dat', 'rb') as f:
#     print(getBlockTxs(f.read()))
# # print(getPropertyDataFromBlock('tx_count', 15))
# from blockchain.mrkl_tree import MerkleTree
# import time

from blockchain.blockchain import Block 
# with open('blockchain/blocks/blk_0001.dat', 'rb') as f:
print(Block.parseBlock(1))
print(Block.parseBlockDigest(1))
