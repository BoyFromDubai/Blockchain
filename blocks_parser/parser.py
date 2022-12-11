import os
from blockchain.blk_structure import *
import hashlib
# class BlockchainParser():

def getPropertyOffset(name):
    res = 0

    for prop, size in block_structure.items():
        if prop == name:
            return res
        else:
            res += size

def getPropertyDataFromBlock(name, n):
    block = getNthBlock(n)
    offset = getPropertyOffset(name)

    return block[offset:offset + block_structure[name]]

def getBlockchainLen(): 
    if os.path.exists('blockchain/blocks'):
        return len(os.listdir('blockchain/blocks')) 
    else:
        os.mkdir('blockchain/blocks')
        return 0

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
    
    return res

def hashInHex(data): return hashlib.sha256(data).hexdigest()

def hashInDigest(data): return hashlib.sha256(data).digest()

def getNthBlock(n):
    with open(f'blockchain/blocks/blk_{str(n + 1).zfill(NUMS_NUM)}.dat', 'rb') as f:
        return f.read()

def getNthBlockHeader(n): return getBlockHeader(getNthBlock(n))

def getNthBlockPrevHash(n): return getNthBlockHeader(n)[:block_structure['prev_blk_hash']]

def hashNthBlockInHex(n): return hashInHex(getNthBlock(n)[block_structure['size']:])

def hashNthBlockInDigest(n): return hashInDigest(getNthBlock(n)[block_structure['size']:])

def getNthBlockTxs(n):  
    block = getNthBlock(n)
    
    txs = {
        'vin': [],
        'vout': []
    }

    txs_num = int.from_bytes(block[getPropertyOffset('tx_count'), block_structure['tx_count']], 'little')
    cur_offset = getPropertyOffset('tx_count') + block_structure['tx_count']
    
    for _ in range(txs_num):
        pass





def getLastBlock(): return getNthBlock(getBlockchainLen() - 1)

def getLastBlockHeader(): return getNthBlockHeader(getBlockchainLen() - 1)

def getLastBlockHash(): return getNthBlockPrevHash(getBlockchainLen() - 1)

def hashLastBlockInHex(): return hashNthBlockInHex(getBlockchainLen() - 1)

def hashLastBlockInDigest(): return hashNthBlockInDigest(getBlockchainLen() - 1)

def getVinsInfo(tx_data, cur_offset):
    vins = []

    cur_offset = block_structure['version']
    vins_field_len = block_structure['input_count']
    vins_num = int.from_bytes(tx_data[cur_offset:cur_offset + vins_field_len], 'little')
    cur_offset += vins_field_len

    for _ in range(vins_num):
        vin = {}
        vin['txid'] = tx_data[cur_offset:cur_offset + block_structure['txid']]
        cur_offset += block_structure['txid']
        vin['vout'] = tx_data[cur_offset:cur_offset + block_structure['vout']]
        cur_offset += block_structure['vout']
        vin['script_sig_size'] = tx_data[cur_offset:cur_offset + block_structure['script_sig_size']]
        # script_sig_size = block_structure['script_sig_size'] 
        script_sig = int.from_bytes(tx_data[cur_offset:cur_offset + vin['script_sig_size']], 'little')
        cur_offset += vin['script_sig_size']
        vin['script_sig'] = tx_data[cur_offset:cur_offset + block_structure['script_sig']]
        cur_offset += script_sig
        vins.append(vin)

    return vins

def getVoutsInfo(tx_data):
    vouts = []
    
    cur_offset = block_structure['version']
    vins_field_len = block_structure['input_count']
    vins_num = int.from_bytes(tx_data[cur_offset:cur_offset + vins_field_len], 'little')
    cur_offset += vins_field_len

    for _ in range(vins_num):
        cur_offset += block_structure['txid']
        cur_offset += block_structure['vout']
        script_sig_size = block_structure['script_sig_size'] 
        script_sig = int.from_bytes(tx_data[cur_offset:cur_offset + script_sig_size], 'little')
        cur_offset += script_sig_size
        cur_offset += script_sig
        
    vouts_field_len = block_structure['output_count']
    vouts_num = int.from_bytes(tx_data[cur_offset:cur_offset + vouts_field_len], 'little')
    cur_offset += vouts_field_len

    for _ in range(vouts_num):
        vout = {}
        value = tx_data[cur_offset:cur_offset + block_structure['value']]
        cur_offset += block_structure['value']
        vout['value'] = value
        script_pub_key_size = tx_data[cur_offset:cur_offset + block_structure['script_pub_key_size']]
        cur_offset += block_structure['script_pub_key_size']
        vout['script_pub_key_size'] = script_pub_key_size
        script_sig = tx_data[cur_offset:cur_offset + int.from_bytes(script_pub_key_size, 'little')]
        cur_offset += int.from_bytes(script_pub_key_size, 'little')
        vout['script_pub_key'] = script_sig

        vouts.append(vout)
    
    return vouts
    






def parseBlock(n):
    block = getNthBlock(n)

    block_info = {}

    cur_offset = 0
    size = int.from_bytes(block[cur_offset:cur_offset + block_structure['size']], 'little')
    cur_offset += block_structure['size']
    block_info['size'] = size
    prev_blk_hash = block[cur_offset:cur_offset + block_structure['prev_blk_hash']].hex()
    cur_offset += block_structure['prev_blk_hash']
    block_info['prev_blk_hash'] = prev_blk_hash
    mrkl_root = block[cur_offset:cur_offset + block_structure['mrkl_root']].hex()
    cur_offset += block_structure['mrkl_root']
    block_info['mrkl_root'] = mrkl_root
    time = int.from_bytes(block[cur_offset:cur_offset + block_structure['time']], 'little')
    cur_offset += block_structure['time']
    block_info['time'] = time
    difficulty = int.from_bytes(block[cur_offset:cur_offset + block_structure['difficulty']], 'little')
    cur_offset += block_structure['difficulty']
    block_info['difficulty'] = difficulty
    nonce = int.from_bytes(block[cur_offset:cur_offset + block_structure['nonce']], 'little')
    cur_offset += block_structure['nonce']
    block_info['time'] = nonce
    tx_count = int.from_bytes(block[cur_offset:cur_offset + block_structure['tx_count']], 'little')
    cur_offset += block_structure['tx_count']
    block_info['tx_count '] = tx_count
    txs = []
    
    for _ in range(tx_count):
        tx = {}
        version = int.from_bytes(block[cur_offset:cur_offset + block_structure['version']], 'little')
        cur_offset += block_structure['version']
        tx['version'] = version
        input_count = int.from_bytes(block[cur_offset:cur_offset + block_structure['input_count']], 'little')
        cur_offset += block_structure['input_count']
        tx['input_count'] = input_count
        vins = []
        
        for __ in range(input_count):
            vin = {}
            txid = int.from_bytes(block[cur_offset:cur_offset + block_structure['txid']], 'little')
            cur_offset += block_structure['txid']
            vin['txid'] = txid
            vout = int.from_bytes(block[cur_offset:cur_offset + block_structure['vout']], 'little')
            cur_offset += block_structure['vout']
            vin['vout'] = vout
            script_sig_size = int.from_bytes(block[cur_offset:cur_offset + block_structure['script_sig_size']], 'little')
            cur_offset += block_structure['script_sig_size']
            vin['script_sig_size'] = script_sig_size
            script_sig = block[cur_offset:cur_offset + script_sig_size].hex()
            cur_offset += script_sig_size
            vin['script_sig'] = script_sig

            vins.append(vin)
        
        tx['vins'] = vins

        output_count = int.from_bytes(block[cur_offset:cur_offset + block_structure['output_count']], 'little')
        cur_offset += block_structure['output_count']
        tx['output_count'] = output_count

        vouts = []

        for __ in range(output_count):
            vout = {}

            value = int.from_bytes(block[cur_offset:cur_offset + block_structure['value']], 'little')
            cur_offset += block_structure['value']
            vout['value'] = value
            script_pub_key_size = int.from_bytes(block[cur_offset:cur_offset + block_structure['script_pub_key_size']], 'little')
            cur_offset += block_structure['script_pub_key_size']
            vout['script_pub_key_size'] = script_pub_key_size
            script_sig = block[cur_offset:cur_offset + script_pub_key_size].hex()
            cur_offset += script_pub_key_size
            vout['script_pub_key'] = script_sig

            vouts.append(vout)

        tx['vouts'] = vouts

        txs.append(tx)

    block_info['txs'] = txs
    
    return block_info
