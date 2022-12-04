NUMS_NUM = 4

block_structure = {
    'size': 4,
    'prev_blk_hash': 32, # header info
    'mrkl_root': 32, # header info
    'time': 4, # header info
    'difficulty': 4, # header info
    'nonce': 4, # header info
    'tx_count': 1,
    'version': 4, #tx info
    'input_count': 1, #tx info
    'txid': 32, #tx info
    'vout': 4, #tx info
    'script_sig_size': None, #tx info
    'script_sig': None, #tx info
    'output_count': 1, #tx info
    'value': 8, #tx info
    'script_pub_key_size': None, #tx info
    'script_pub_key': None, #tx info
    'locktime': 4, #tx info
}