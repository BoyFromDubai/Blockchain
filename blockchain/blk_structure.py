NUMS_NUM = 4

# blk_structure = [
#     4, # size
#     36, # prev_blk_hash
#     68, # mrkl_root
#     72, # time
#     76, # difficulty
#     80, # nonce
#     81, # 
#     85, # 
#     86, # 
#     118, # 
#     122, # 
#     # # 
#     # # 
#     123, # 
#     131, # 
#     135, # 
#     139 # 
# ]

block_structure = {
    'size': 4,
    'prev_blk_hash': 32, # header info      little
    'mrkl_root': 32, # header info          little
    'time': 4, # header info                little
    'difficulty': 4, # header info          little
    'nonce': 4, # header info               little
    'tx_count': 1, #                        little
    'version': 4, #tx info                  little
    'input_count': 1, #tx info              little
    'txid': 32, #tx info                    little
    'vout': 4, #tx info                     little
    'script_sig_size': 8, #tx info          little
    'script_sig': None, #tx info              
    'output_count': 1, #tx info             little
    'value': 8, #tx info                    little
    'script_pub_key_size': 8, #tx info      little
    'script_pub_key': None, #tx info        
    'locktime': 4, #tx info                 little
}