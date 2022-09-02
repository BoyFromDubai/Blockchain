import json
import os

NUMS_NUM = 4

block_structure = {
    'size': 4,
    'header': {
        'prev_blk_hash': 32,
        'mrkl_root': 32,
        'time': 4,
        'difficulty': 4,
        'nonce': 4
    },
    'tx_count': 1,
    'tx_data': {
        'version': 4,
        'input_count': 1,
        'input': {
            'txid': 32,
            'vout': 4,
            # 'script_sig_size': None,
            # 'script_sig': None,
        },
        'output_count': 1,
        'output': {
            'value': 8,
            # 'script_pub_key_size': None,
            # 'script_pub_key': None
        },
        'locktime': 4,
    }
}

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
            # chain.append({
            #     'time': ,
            # })
            f.close()

    except:
        os.mkdir(f'blockchain/{dir_name}')
    
    return chain

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

