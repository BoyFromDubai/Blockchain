import sqlite3

def get_db_connection():
    conn = sqlite3.connect('database/database.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_chain_from_db(blockchain):
    connection = get_db_connection()

    with open('database/tables.sql') as f:
        connection.executescript(f.read())

    connection.commit()
    connection.close()

def add_transaction_to_mempool(tx):
    connection = get_db_connection()
    cur = connection.cursor()

    cur.execute("INSERT OR IGNORE INTO mempool(vers, locktime) VALUES(?, ?)", 
    (tx['version'], tx['locktime'])
    )

    last_id = cur.execute("SELECT last_insert_rowid()").fetchall()[0][0]
    for vin in tx['vin']:
        cur.execute("INSERT OR IGNORE INTO mempool_vins(tx_index, tx_id, vout, asm, hex, sequencee) VALUES(?, ?, ?, ?, ?, ?)", 
        (last_id, vin['txid'], vin['vout'], vin['scriptSig']['asm'], vin['scriptSig']['hex'], vin['sequence'])
        )
    for vout in tx['vout']:
        cur.execute("INSERT OR IGNORE INTO mempool_vouts(tx_index, coins, n, asm, hex, req_sigs, addresses) VALUES(?, ?, ?, ?, ?, ?, ?)", 
        (last_id, vout['value'], vout['n'], vout['scriptPubSig']['asm'], vout['scriptPubSig']['hex'], vout['scriptPubSig']['reqSigs'], vout['scriptPubSig']['addresses'])
        )

    connection.commit()
    connection.close()

def get_mempool():
    connection = get_db_connection()
    cur = connection.cursor()
    mempool = connection.execute('SELECT * FROM mempool').fetchall()

    from main import blockchain
    for tx in mempool:
        addresses = connection.execute(f'SELECT addresses FROM mempool_vouts WHERE tx_index={tx["id"]}').fetchall()
        n = connection.execute(f'SELECT n FROM mempool_vouts WHERE tx_index={tx["id"]}').fetchall()
        value = connection.execute(f'SELECT coins FROM mempool_vouts WHERE tx_index={tx["id"]}').fetchall()
        tx_id = connection.execute(f'SELECT tx_id FROM mempool_vins WHERE tx_index={tx["id"]}').fetchall()
        vout = connection.execute(f'SELECT vout FROM mempool_vins WHERE tx_index={tx["id"]}').fetchall()
        transaction = blockchain.create_transaction(value, addresses, tx_id, vout)





def save_block(block):
    connection = get_db_connection()
    cur = connection.cursor()

    cur.execute("INSERT OR IGNORE INTO chain VALUES(?, ?, ?, ?, ?, ?, ?)", 
    (block['index'], block['header']['timestamp'], block['header']['prev_hash'], 
    block['header']['mrkl_root'], block['header']['nonce'], block['header']['difficulty'], 
    block['transaction_counter'])
    )
    for i in range(len(block['transactions'])):
        tx = block['transactions'][i]
        cur.execute("INSERT OR IGNORE INTO transactions(block_index, vers, locktime) VALUES(?, ?, ?)", 
        (block['index'], tx['version'], tx['locktime'])
        )

        last_id = cur.execute("SELECT last_insert_rowid()").fetchall()[0][0]
        for vin in tx['vin']:
            cur.execute("INSERT OR IGNORE INTO vins(tx_index, tx_id, vout, asm, hex, sequencee) VALUES(?, ?, ?, ?, ?, ?)", 
            (last_id, vin['txid'], vin['vout'], vin['scriptSig']['asm'], vin['scriptSig']['hex'], vin['sequence'])
            )
        for vout in tx['vout']:
            cur.execute("INSERT OR IGNORE INTO vouts(tx_index, coins, n, asm, hex, req_sigs, addresses) VALUES(?, ?, ?, ?, ?, ?, ?)", 
            (last_id, vout['value'], vout['n'], vout['scriptPubSig']['asm'], vout['scriptPubSig']['hex'], vout['scriptPubSig']['reqSigs'], vout['scriptPubSig']['addresses'])
            )    

    print(connection.execute('SELECT * FROM chain').fetchall()[0])

    connection.commit()
    connection.close()

