PKG_TYPE_SIZE = 4
PKG_TYPE_VARS = {
    'version':          b'\x00\x00\x00\x00',
    'blocks_request':           b'\x00\x00\x00\x01',
    'blocks_ack':           b'\x00\x00\x00\x02',
    'blocks_finished':           b'\x00\x00\x00\x03',
    
    'send_tx':              b'\x00\x00\x00\x04',
    'ask_last_block_id':    b'\x00\x00\x00\x05',
    'get_last_block_id':    b'\x00\x00\x00\x06',

    'peers_request':        b'\x00\x00\x00\x07',
    'peers_ack':           b'\x00\x00\x00\x08',

    'stop_signal':     b'\x00\x00\xFF\xFF',
}
HASH_OFFSET = 4
HASH_SIZE = 16

DATA_LEN_SIZE = 4


BUF_SIZE = 10
