import json
import os
from re import T
from time import time

from itsdangerous import exc

NUMS_NUM = 4


def save_block(block):
    file = f"blockchain/blocks/blk_{str(block['index']).zfill(NUMS_NUM)}.json"
    f = open(file, 'w')
    f.write(json.dumps(block))
    f.close()

    # file = f"blockchain/bbblocks/blk_{str(block['index']).zfill(NUMS_NUM)}.dat"
    # f = open(file, 'wb')
    

def save_to_mempool(tx):
    mempool_path = "blockchain/mempool/"
    file_path = mempool_path + "mempool.json"
    
    if not os.path.exists(mempool_path):
        os.mkdir(mempool_path)
        
        if not os.path.exists(file_path):
            with open(file_path, 'w'): pass

    cur_size = os.stat("blockchain/mempool/mempool.json").st_size
    if cur_size == 0:
        f = open(file_path, 'a')
        json.dump({'tx': [tx]}, f)
        f.close()
    else:
        f = open(file_path, 'r+')
        cur_mempool = json.load(f)
        cur_mempool['tx'].append(tx)
        f.seek(0)
        json.dump(cur_mempool, f, indent=4)
        f.close()

def get_chain():
    chain = []
    dir_name = 'blocks'

    try:
        files_arr = sorted(os.listdir(f'blockchain/{dir_name}'))
        
        for file in files_arr:
            f = open('blockchain/blocks/' + file, 'r')
            chain.append(json.load(f))
            f.close()

    except:
        os.mkdir(f'blockchain/{dir_name}')
    
    return chain

def get_last_block():
    last_file = sorted(os.listdir('blockchain/blocks'))[-1]
    f = open('blockchain/blocks/' + last_file, 'r')
    last_block = json.load(f)
    f.close()

    return last_block

def get_block(index):
    block_file = sorted(os.listdir('blockchain/blocks'))[index - 1]
    f = open('blockchain/blocks/' + block_file, 'r')
    block = json.load(f)
    f.close()

    return block

def get_mempool():
    mempool = []

    file = "blockchain/mempool/mempool.json"
    cur_size = os.stat(file).st_size
    f = open(file, 'r')
    if not cur_size == 0:
        data = json.load(f)
        mempool = data['tx']
    f.close()

    return mempool

def clear_mempool():
    file = "blockchain/mempool/mempool.json"
    f = open(file, 'r+')
    f.truncate(0)
    f.close()
    
