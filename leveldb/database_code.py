from blocks_parser.parser import *


VOUT_STRUCT = {
    'height': 4,
    'vouts_num': 1,
    'spent': 1, 
    'value': 8, 
    'script_pub_key_size': 8,
    'script_pub_key': None, 
}

def createVoutsStruct(txid, n, tx_info, wallet):
    vouts = getVoutsInfo(tx_info)
    res = getBlockchainLen().to_bytes(VOUT_STRUCT['height'], 'little')
    res += len(vouts).to_bytes(VOUT_STRUCT['vouts_num'], 'little')
    
    for i in range(len(vouts)):
        res += (0).to_bytes(VOUT_STRUCT['spent'], 'little')
        res += vouts[i]['value']
        res += vouts[i]['script_pub_key_size']
        res += vouts[i]['script_pub_key']

        if wallet.pk.to_string() == vouts[i]['script_pub_key']:
            wallet.appendUTXO(txid, n.to_bytes(1, 'little'), vouts[i]['value'])

    return res
