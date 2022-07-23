import json
import os

NUMS_NUM = 4

block_structure = {
    'size': 4,
    'header': {
        'version': 4,
        'prev_blk_hash': 32,
        'mrkl_root': 32,
        'time': 4,
        'bits': 4,
        'nonce': 4
    },
    'tx_count': 2,
    'tx_data': {
        'version': 4,
        'input_count': 2,
        'input': {
            'txid': 32,
            'vout': 4,
            'script_sig_size': None,
            'script_sig': None,
        },
        'output_count': 2,
        'output': {
            'value': 8,
            'script_pub_key_size': None,
            'script_pub_key': None
        }
    }
}

def save_block(block):
    file = f"blockchain/blocks/blk_{str(block['index']).zfill(NUMS_NUM)}.json"
    f = open(file, 'w')
    f.write(json.dumps(block))
    f.close()
    print(block)
    block_to_bytes(block)

    
def block_to_bytes(block):
    file = f"baa.txt"
    f = open(file, 'wb')
    f.write((bytes.fromhex(block['header']['prev_hash'])))
    f.close()

def save_to_mempool(tx):
    file = "blockchain/mempool/mempool.json"

    cur_size = os.stat("blockchain/mempool/mempool.json").st_size
    if cur_size == 0:
        f = open(file, 'a')
        json.dump({'tx': [tx]}, f)
        f.close()
    else:
        f = open(file, 'r+')
        cur_mempool = json.load(f)
        cur_mempool['tx'].append(tx)
        f.seek(0)
        json.dump(cur_mempool, f, indent=4)
        f.close()

def get_chain():
    chain = []
    files_arr = os.listdir('blockchain/blocks')
    for file in files_arr:
        f = open('blockchain/blocks/' + file, 'r')
        chain.append(json.load(f))
        f.close()
    return chain

def get_last_block():
    last_file = os.listdir('blockchain/blocks')[-1]
    f = open('blockchain/blocks/' + last_file, 'r')
    last_block = json.load(f)
    f.close()

    return last_block

def get_block(index):
    block_file = os.listdir('blockchain/blocks')[index - 1]
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
    
