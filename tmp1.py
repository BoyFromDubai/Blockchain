# with open('blockchain/blocks/blk_0001.dat', 'rb') as f:
#     print(f.read())

from blocks_parser.parser import *
import json
# getNthBlockTxs(9)



with open('tmp.json', 'w') as f:
    json.dump(parseBlock(7), f)

print(parseBlock(7))
