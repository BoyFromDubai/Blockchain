from core.blockchain.constants import *
from core.miner.miner import Miner 
from core.wallet.wallet import Wallet
from core.database.db import DB
from core.blockchain.transactions.vin import Vin
from core.blockchain.transactions.vout import Vout

import hashlib
import os

class Blockchain():
    SIZE_OF_BLOCK = 4
    MEMPOOL_TX_SIZE_INFO = 2

    def __init__(self) -> None:
        self.miner = Miner(self)
        self.wallet = Wallet()
        self.db = DB()

        if not self.get_chain_len():
             self.__append_block(b'\xa9\xd1\xc5\xb6GjY\x9b\x9a\xd2\xa2\x1djw\xba\x94\x13_q\xc0\x8a0x@\xe0\xe1\xcf\xbb\xfe\x0b\xba\xad\x00\x00\x00\x00\x00\x00\x00\x00'
             b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00m/\x9fc\x01\x00\x00\x00\x01\x00\x00\x00\x00') #TODO: change prev_hash
        pass
    
    def __append_block(self, block_info):
        res = len(block_info).to_bytes(Blockchain.SIZE_OF_BLOCK, 'little')
        res += block_info
        with open(f"blockchain/blocks/blk_{str(self.get_chain_len()).zfill(NUM_OF_NUMBERS_IN_BLK_FILE)}.dat", 'wb') as f:
            f.write(res)

    def get_mempool(self):
        transactions = []

        with open('core/blockchain/mempool.dat', 'rb') as f:
            all_data = f.read()

            f.seek(0)

            while f.tell() < len(all_data):
                tx_info_len = int.from_bytes(f.read(self.MEMPOOL_TX_SIZE_INFO), 'little')
                transactions.append(f.read(tx_info_len))

        return transactions

    def mine_block(self):
        blk_data = self.miner.mine_block(self.wallet.pk)
        txs = self.parse_block_txs(blk_data)
        
        for tx in txs:
            vins = Blockchain.parse_vins(tx)
            vouts = Blockchain.parse_vouts(tx)
            cur_txid = hashlib.sha256(tx).digest()
            
            self.db.add_tx_to_db(self.get_chain_len(), cur_txid, vins, vouts)

    def create_transaction(self, vout_data, vin_data = []):
        version = (0).to_bytes(BLOCK_STRUCT['version'], "little")
        tx_data = version
        inputs_num = len(vin_data).to_bytes(BLOCK_STRUCT['input_count'], "little")
        tx_data += inputs_num

        if len(vin_data):
            coins_to_spend = sum(map(lambda value: int(value), [info_for_vout[1] for info_for_vout in vout_data]))
            txids_in_bytes = [(int(txid, 16).to_bytes(BLOCK_STRUCT['txid'], 'big'), int(vout)) for txid, vout in vin_data]
            available_coins = sum(list(map(lambda data: int.from_bytes(self.db.getInfoOfTxid(data[0])['vouts'][data[1]]['value'], 'little'), txids_in_bytes)))

            if available_coins < coins_to_spend:
                raise ValueError('[ERROR] Not enough coins on these vins!!!')

            
        for i in range(len(vin_data)):
            # tx_data += self.__create_vin(vin_data[i][0], int(vin_data[i][1]))
            tx_data += Vin(vin_data[i][0], int(vin_data[i][1])).vin_data

        tx_data += len(vout_data).to_bytes(1, "little") #outputs num

        for i in range(len(vout_data)):
            print(vout_data[i])
            tx_data += Vout(vout_data[i][0], int(vout_data[i][1])).vout_data
            # tx_data += self.__create_vout(vout_data[i][0], int(vout_data[i][1]))
        
        if len(vin_data):
            self.appendToMempool(tx_data)
                
        return tx_data

    def verifyChain(self):
        block_files = self.get_block_files()
        prev_blk_hash = Blockchain.hash_nth_block_in_digest(0)
        
        for i in range(1, len(block_files)):
            cur_blk_prev_hash = self.get_nth_block_prev_hash_field(i)

            if prev_blk_hash != cur_blk_prev_hash:
                return False
            else:
                prev_blk_hash = self.hash_nth_block_in_digest(i)

            block_txs = self.parse_nth_block_txs(i)

            for tx in block_txs:
                vouts = self.parse_vouts(tx)

                for i in range(len(vouts)):

                    if vouts[i]['script_pub_key'].hex() == self.wallet.sk.get_verifying_key().to_string().hex():
                        self.wallet.appendUTXO(hashlib.sha256(tx).digest(), i, vouts[i]['value'])
            
        return True

    @staticmethod
    def get_block_files(): return sorted(os.listdir('blockchain/blocks'))

    @staticmethod
    def get_chain_len():
        if os.path.exists('blockchain/blocks'):
            # files_in_dir_len = len(os.listdir('blockchain/blocks'))
            # return math.ceil(files_in_dir_len / 2) if files_in_dir_len > 1 else files_in_dir_len
            return len(os.listdir('blockchain/blocks'))
        else:
            os.mkdir('blockchain/blocks')
            return 0

    @staticmethod
    def get_block_header(data):
        cur_offset = 0
        
        for key in BLOCK_STRUCT:
            if key == 'tx_count':
                break
            cur_offset += BLOCK_STRUCT[key]
        
        return data[:cur_offset]

    @staticmethod
    def get_block_exact_field(data, field_name):
        header = Blockchain.get_block_header(data)
        cur_offset = 0
        cur_size = 0

        for key in BLOCK_STRUCT:
            if key == 'mrkl_root':
                cur_size = BLOCK_STRUCT[key]
                break
            else:
                cur_offset += BLOCK_STRUCT[key]

        return header[cur_offset:cur_offset + cur_size] 

    @staticmethod
    def get_block_mrkl_root_field(data): return Blockchain.get_block_exact_field(data, 'mrkl_root')
    
    @staticmethod
    def get_block_prev_hash_field(data): return Blockchain.get_block_exact_field(data, 'prev_blk_hash')
    
    @staticmethod
    def get_nth_block_header(n): return Blockchain.get_block_header(Blockchain.get_nth_block(n))
        
    @staticmethod
    def get_nth_block_prev_hash_field(n): return Blockchain.get_block_prev_hash_field(Blockchain.get_nth_block(n))

    @staticmethod
    def get_nth_block(n):
        with open(f'blockchain/blocks/blk_{str(n).zfill(NUM_OF_NUMBERS_IN_BLK_FILE)}.dat', 'rb') as f:
            blk_size = int.from_bytes(f.read(Blockchain.SIZE_OF_BLOCK), 'little')

            return f.read(blk_size)

    @staticmethod
    def parse_vins(tx_data):
        vins = []

        cur_offset = BLOCK_STRUCT['version']
        vins_field_len = BLOCK_STRUCT['input_count']
        vins_num = int.from_bytes(tx_data[cur_offset:cur_offset + vins_field_len], 'little')
        cur_offset += vins_field_len

        for _ in range(vins_num):
            vin = {}
            vin['txid'] = tx_data[cur_offset:cur_offset + BLOCK_STRUCT['txid']]
            cur_offset += BLOCK_STRUCT['txid']
            vin['vout'] = tx_data[cur_offset:cur_offset + BLOCK_STRUCT['vout']]
            cur_offset += BLOCK_STRUCT['vout']
            vin['script_sig_size'] = tx_data[cur_offset:cur_offset + BLOCK_STRUCT['script_sig_size']]
            # script_sig = tx_data[cur_offset:cur_offset + vin['script_sig_size']]
            cur_offset += BLOCK_STRUCT['script_sig_size']
            vin['script_sig'] = tx_data[cur_offset:cur_offset + int.from_bytes(vin['script_sig_size'], 'little')]
            cur_offset += int.from_bytes(vin['script_sig_size'], 'little')
            vins.append(vin)

        return vins

    @staticmethod
    def get_vouts_data_offset(tx_data):
        cur_offset = BLOCK_STRUCT['version']
        vins_num = int.from_bytes(tx_data[cur_offset:cur_offset + BLOCK_STRUCT['input_count']], 'little')
        cur_offset += BLOCK_STRUCT['input_count']

        for _ in range(vins_num):
            cur_offset += BLOCK_STRUCT['txid']
            cur_offset += BLOCK_STRUCT['vout']
            script_sig_size = int.from_bytes(tx_data[cur_offset:cur_offset + BLOCK_STRUCT['script_sig_size']], 'little')
            cur_offset += BLOCK_STRUCT['script_sig_size']
            cur_offset += script_sig_size

        return cur_offset

    @staticmethod
    def parse_vouts(tx_data):
        vouts_offset = Blockchain.get_vouts_data_offset(tx_data)

        vouts_info = tx_data[vouts_offset:]
        cur_offset = 0
        vouts_field_len = BLOCK_STRUCT['output_count']
        vouts_num = int.from_bytes(vouts_info[cur_offset:cur_offset + vouts_field_len], 'little')
        cur_offset += vouts_field_len
        vouts = []

        for _ in range(vouts_num):
            vout = {}
            value = vouts_info[cur_offset:cur_offset + BLOCK_STRUCT['value']]
            cur_offset += BLOCK_STRUCT['value']
            vout['value'] = value
            script_pub_key_size = vouts_info[cur_offset:cur_offset + BLOCK_STRUCT['script_pub_key_size']]
            cur_offset += BLOCK_STRUCT['script_pub_key_size']
            vout['script_pub_key_size'] = script_pub_key_size
            script_sig = vouts_info[cur_offset:cur_offset + int.from_bytes(script_pub_key_size, 'little')]
            cur_offset += int.from_bytes(script_pub_key_size, 'little')
            vout['script_pub_key'] = script_sig

            vouts.append(vout)
        
        return vouts

    @staticmethod
    def parse_nth_block_txs(n):
        block = Blockchain.get_nth_block(n)
        header = Blockchain.get_nth_block_header(n)

        txs_data = block[len(header):] 
        
        return Blockchain.parse_block_txs(txs_data)

    @staticmethod
    def parse_block_txs(data):
        data = data[Blockchain.get_block_header(data):]

        tx_count = int.from_bytes(data[:BLOCK_STRUCT['tx_count']], 'little')
        cur_offset = BLOCK_STRUCT['tx_count']
        # BlkTransactions.TXS_STRUCT['tx_count'] = tx_count
        txs = []
    
        for _ in range(tx_count):
            tx = b''
            version = data[cur_offset:cur_offset + BLOCK_STRUCT['version']]
            cur_offset += BLOCK_STRUCT['version']
            tx += version
            input_count = data[cur_offset:cur_offset + BLOCK_STRUCT['input_count']]
            cur_offset += BLOCK_STRUCT['input_count']
            tx += input_count
            
            for __ in range(int.from_bytes(input_count, 'little')):
                vin = b''
                txid = data[cur_offset:cur_offset + BLOCK_STRUCT['txid']]
                cur_offset += BLOCK_STRUCT['txid']
                vin += txid
                vout = data[cur_offset:cur_offset + BLOCK_STRUCT['vout']]
                cur_offset += BLOCK_STRUCT['vout']
                vin += vout
                script_sig_size = data[cur_offset:cur_offset + BLOCK_STRUCT['script_sig_size']]
                cur_offset += BLOCK_STRUCT['script_sig_size']
                vin += script_sig_size
                script_sig = data[cur_offset:cur_offset + int.from_bytes(script_sig_size, 'little')]
                cur_offset += int.from_bytes(script_sig_size, 'little')
                vin += script_sig

                tx += vin
            
            output_count = data[cur_offset:cur_offset + BLOCK_STRUCT['output_count']]
            cur_offset += BLOCK_STRUCT['output_count']
            tx += output_count

            for __ in range(int.from_bytes(output_count, 'little')):
                vout = b''

                value = data[cur_offset:cur_offset + BLOCK_STRUCT['value']]
                cur_offset += BLOCK_STRUCT['value']
                vout += value
                script_pub_key_size = data[cur_offset:cur_offset + BLOCK_STRUCT['script_pub_key_size']]
                cur_offset += BLOCK_STRUCT['script_pub_key_size']
                vout += script_pub_key_size
                script_sig = data[cur_offset:cur_offset + int.from_bytes(script_pub_key_size, 'little')]
                cur_offset += int.from_bytes(script_pub_key_size, 'little')
                vout += script_sig

                tx += vout

            txs.append(tx)

        return txs
        

    @staticmethod
    def hash_nth_block_in_digest(n): return hashlib.sha256(Blockchain.get_nth_block_header(n)).digest()

    @staticmethod
    def hash_nth_block_in_hexdigest(n): return hashlib.sha256(Blockchain.get_nth_block_header(n)).hexdigest()

    @staticmethod
    def hash_last_block_in_digest(): return hashlib.sha256(Blockchain.get_nth_block_header(Blockchain.get_chain_len() - 1)).digest()

    @staticmethod
    def hash_last_block_in_hexdigest(): return hashlib.sha256(Blockchain.get_nth_block_header(Blockchain.get_chain_len() - 1)).hexdigest()