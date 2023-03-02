PKG_TYPE_SIZE = 4
PKG_TYPE_VARS = {
    'version_request':          b'\x00\x00\x00\x00',
    'version_ack':         b'\x00\x00\x00\x01',
    'get_blocks':           b'\x00\x00\x00\x02',
    'send_block':           b'\x00\x00\x00\x03',
    'send_tx':              b'\x00\x00\x00\x04',
    'ask_last_block_id':    b'\x00\x00\x00\x05',
    'get_last_block_id':    b'\x00\x00\x00\x06',

    'peers_request':        b'\x00\x00\x00\x07',
    'peers_ack':           b'\x00\x00\x00\x08',

    'send_stop_signal':     b'\x00\x00\xFF\xFF',
}
HASH_OFFSET = 4
HASH_SIZE = 16

DATA_LEN_SIZE = 4


BUF_SIZE = 10
