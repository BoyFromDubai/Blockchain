import os

class Mempool:
    MEMPOOL_DIR = 'mempool'
    MEMPOOL_PATH = os.path.join(MEMPOOL_DIR, 'mempool.dat')
    TX_SIZE = 2

    def __init__(self, blockchain) -> None:
        self.blockchain = blockchain
        
        if not os.path.exists(self.MEMPOOL_PATH):
            os.mkdir(self.MEMPOOL_DIR)

            with open(self.MEMPOOL_PATH, 'wb'):
                pass

    def add_tx(self, tx_data: bytes):
        with open(Mempool.MEMPOOL_PATH, 'ab') as f:
            f.write(len(tx_data).to_bytes(Mempool.TX_SIZE, 'little'))
            f.write(tx_data)


    def clear_mempool(self):
        with open(self.MEMPOOL_PATH, 'wb'): 
            pass

    def get_mempool(self):
        transactions = []

        with open(self.MEMPOOL_PATH, 'rb') as f:
            all_data = f.read()

            f.seek(0)

            while f.tell() < len(all_data):
                tx_info_len = int.from_bytes(f.read(self.TX_SIZE), 'little')
                transactions.append(f.read(tx_info_len))

        return transactions
