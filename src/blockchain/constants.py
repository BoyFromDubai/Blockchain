BLOCK_STRUCT = {
    'prev_blk_hash': 32, # header info      little
    'mrkl_root': 32, # header info          little
    'time': 4, # header info                little
    'difficulty': 4, # header info          little
    'nonce': 4, # header info               little
    'tx_count':             1,      #                        little
    'version':              4,      #tx info                  little
    'input_count':          1,      #tx info              little
    'txid':                 32,     #tx info                    little
    'vout':                 4,      #tx info                     little
    'script_sig_size':      8,      #tx info          little
    'script_sig':           None,   #tx info              
    'output_count':         1,      #tx info             little
    'value':                8,      #tx info                    little
    'script_pub_key_size':  8,      #tx info      little
    'script_pub_key':       None,   #tx info        
}

NUMS_IN_NAME = 4
SIZE = 4
