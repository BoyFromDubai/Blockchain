PKG_TYPE_SIZE = 4
PKG_TYPE_VARS = {
    'version':          b'\x00\x00\x00\x00',
    'get_blocks':           b'\x00\x00\x00\x01',
    'send_block':           b'\x00\x00\x00\x02',
    'send_tx':              b'\x00\x00\x00\x03',
    'ask_last_block_id':    b'\x00\x00\x00\x04',
    'get_last_block_id':    b'\x00\x00\x00\x05',

    'peers_request':        b'\x00\x00\x00\x06',
    'peers_ack':           b'\x00\x00\x00\x07',

    'stop_signal':     b'\x00\x00\xFF\xFF',
}
HASH_OFFSET = 4
HASH_SIZE = 16

DATA_LEN_SIZE = 4


BUF_SIZE = 10
