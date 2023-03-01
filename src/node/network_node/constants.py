PKG_TYPE_SIZE = 4
PKG_TYPE_VARS = {
    'ask_version':          b'\x00\x00\x00\x00',
    'send_version':          b'\x00\x00\x00\x00',
    'get_blocks':       b'\x00\x00\x00\x01',
    'send_block':            b'\x00\x00\x00\x02',
    'send_tx':               b'\x00\x00\x00\x03',
    'ask_last_block_id':    b'\x00\x00\x00\x04',
    'get_last_block_id':    b'\x00\x00\x00\x04',

    'ask_for_peers':            b'\x00\x00\x00\x05',
    'send_peers':            b'\x00\x00\x00\x05',

    'send_stop_socket':      b'\x00\x00\xFF\xFF',
}
HASH_OFFSET = 4
HASH_SIZE = 32

DATA_LEN_SIZE = 16


BUF_SIZE = 51
