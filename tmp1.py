# with open('blockchain/blocks/blk_0000.dat', 'rb') as f:
#     print(f.read())

from blockchain.blockchain import Block 
# with open('blockchain/blocks/blk_0001.dat', 'rb') as f:
print(Block.parseBlock(1))
