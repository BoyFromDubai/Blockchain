with open('blockchain/blocks/blk_0001.dat', 'rb') as f:
    print(f.read())

from blocks_parser.parser import *
import json
getNthBlockTxs(2)

with open('tmp.json', 'w') as f:
    json.dump(parseBlock(14), f)

print(getPropertyDataFromBlock('tx_count', 15))
