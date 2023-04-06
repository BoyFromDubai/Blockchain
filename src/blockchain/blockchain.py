from .constants import *
from .mempool import Mempool
from .chainstate_db import ChainStateDB
from .transaction import Transaction
from ..merkle_tree import MerkleTree

import ecdsa
from typing import List
import hashlib
import os


class Blockchain:
    BLOCKS_DIR = 'blocks'

    def __init__(self):
        self.mempool = Mempool(self)
        self.chainstate_db = ChainStateDB(self)

        if not self.__blocks_folder_existance():
            os.mkdir(self.BLOCKS_DIR)

            with open(os.path.join(self.BLOCKS_DIR, f'blk_{str(0).zfill(NUMS_IN_NAME)}.dat'), 'wb') as f:
                genezis_block = b'M\x00\x00\x00\xa9\xd1\xc5\xb6GjY\x9b\x9a\xd2\xa2\x1djw\xba\x94\x13_q\xc0\x8a0x@\xe0\xe1\xcf\xbb\xfe\x0b\xba\xad\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00m/\x9fc\x01\x00\x00\x00\x01\x00\x00\x00\x00'
                f.write(genezis_block)

    def __blocks_folder_existance(self): return os.path.exists(self.BLOCKS_DIR)

    def __create_rev_file(self, txs : dict):
        pass
        # for tx in txs:
        #     vins = self.get_vins(tx)
            # txid = hashlib.sha256(tx).digest()
            # utxo = self.db.get_utxo_formatted(txid)

    def get_new_block_from_peer(self, index: int, blk_data: bytes):
        txs = self.get_block_txs(blk_data)

        if self.__check_block_correctness(index, blk_data, txs):
            self.__create_rev_file(txs)
            self.__update_db(txs)
            self.__save_block(index, blk_data)

        else:
            raise Exception('[ERROR]: New Block was falsified')

    def get_new_tx_from_peer(self, tx_data: bytes):
        if self.__verify_transaction(tx_data):
            self.__append_to_mempool(tx_data)
        
        else:
            raise Exception('[EEROR] Transaction is not valid')

    def get_property_offset(self, property_name: str):
        cur_offset = 0

        for key, value in BLOCK_STRUCT.items():
            if key == property_name:
                return cur_offset
            else:
                cur_offset += value

        return False

    def get_nth_block(self, n: int):
        with open(f'{self.BLOCKS_DIR}/blk_{str(n).zfill(NUMS_IN_NAME)}.dat', 'rb') as f:
            blk_size = int.from_bytes(f.read(SIZE), 'little')
            return f.read(blk_size)

    def hash_nth_block_in_digest(self, n: int):
        return hashlib.sha256(self.get_nth_block_header(n)).digest()

    def hash_nth_block_in_hexdigest(self, n: int):
        return hashlib.sha256(self.get_nth_block_header(n)).hexdigest()

    def hash_last_block_in_digest(self):
        return hashlib.sha256(self.get_nth_block_header(self.get_chain_len() - 1)).digest()

    def hash_last_block_in_hexdigest(self):
        return hashlib.sha256(self.get_nth_block_header(self.get_chain_len() - 1)).hexdigest()

    def parse_block(self, blk_data : bytes):
        block_info = {}

        cur_offset = 0
        prev_blk_hash = blk_data[cur_offset:cur_offset + BLOCK_STRUCT['prev_blk_hash']].hex()
        cur_offset += BLOCK_STRUCT['prev_blk_hash']
        block_info['prev_blk_hash'] = prev_blk_hash
        mrkl_root = blk_data[cur_offset:cur_offset + BLOCK_STRUCT['mrkl_root']].hex()
        cur_offset += BLOCK_STRUCT['mrkl_root']
        block_info['mrkl_root'] = mrkl_root
        time = int.from_bytes(blk_data[cur_offset:cur_offset + BLOCK_STRUCT['time']], 'little')
        cur_offset += BLOCK_STRUCT['time']
        block_info['time'] = time
        difficulty = int.from_bytes(blk_data[cur_offset:cur_offset + BLOCK_STRUCT['difficulty']], 'little')
        cur_offset += BLOCK_STRUCT['difficulty']
        block_info['difficulty'] = difficulty
        nonce = int.from_bytes(blk_data[cur_offset:cur_offset + BLOCK_STRUCT['nonce']], 'little')
        cur_offset += BLOCK_STRUCT['nonce']
        block_info['nonce'] = nonce
        tx_count = int.from_bytes(blk_data[cur_offset:cur_offset + BLOCK_STRUCT['tx_count']], 'little')
        cur_offset += BLOCK_STRUCT['tx_count']
        block_info['tx_count '] = tx_count
        txs = []
        
        for _ in range(tx_count):
            tx = {}
            version = int.from_bytes(blk_data[cur_offset:cur_offset + BLOCK_STRUCT['version']], 'little')
            cur_offset += BLOCK_STRUCT['version']
            tx['version'] = version
            input_count = int.from_bytes(blk_data[cur_offset:cur_offset + BLOCK_STRUCT['input_count']], 'little')
            cur_offset += BLOCK_STRUCT['input_count']
            tx['input_count'] = input_count
            vins = []
            
            for __ in range(input_count):
                vin = {}
                txid = hex(int.from_bytes(blk_data[cur_offset:cur_offset + BLOCK_STRUCT['txid']], 'little'))[2:]
                cur_offset += BLOCK_STRUCT['txid']
                vin['txid'] = txid
                vout = int.from_bytes(blk_data[cur_offset:cur_offset + BLOCK_STRUCT['vout']], 'little')
                cur_offset += BLOCK_STRUCT['vout']
                vin['vout'] = vout
                script_sig_size = int.from_bytes(blk_data[cur_offset:cur_offset + BLOCK_STRUCT['script_sig_size']], 'little')
                cur_offset += BLOCK_STRUCT['script_sig_size']
                vin['script_sig_size'] = script_sig_size
                script_sig = blk_data[cur_offset:cur_offset + script_sig_size].hex()
                cur_offset += script_sig_size
                vin['script_sig'] = script_sig

                vins.append(vin)
            
            tx['vins'] = vins

            output_count = int.from_bytes(blk_data[cur_offset:cur_offset + BLOCK_STRUCT['output_count']], 'little')
            cur_offset += BLOCK_STRUCT['output_count']
            tx['output_count'] = output_count

            vouts = []

            for __ in range(output_count):
                vout = {}

                value = int.from_bytes(blk_data[cur_offset:cur_offset + BLOCK_STRUCT['value']], 'little')
                cur_offset += BLOCK_STRUCT['value']
                vout['value'] = value
                script_pub_key_size = int.from_bytes(blk_data[cur_offset:cur_offset + BLOCK_STRUCT['script_pub_key_size']], 'little')
                cur_offset += BLOCK_STRUCT['script_pub_key_size']
                vout['script_pub_key_size'] = script_pub_key_size
                script_sig = blk_data[cur_offset:cur_offset + script_pub_key_size].hex()
                cur_offset += script_pub_key_size
                vout['script_pub_key'] = script_sig

                vouts.append(vout)

            tx['vouts'] = vouts

            txs.append(tx)

        block_info['txs'] = txs
        
        return block_info

    def parse_nth_block(self, n : int):
        return self.parse_block(self.get_nth_block(n))

    def parse_block_digest(self, blk_data : bytes):
        block_info = {}

        cur_offset = 0
        prev_blk_hash = blk_data[cur_offset:cur_offset + BLOCK_STRUCT['prev_blk_hash']]
        cur_offset += BLOCK_STRUCT['prev_blk_hash']
        block_info['prev_blk_hash'] = prev_blk_hash
        mrkl_root = blk_data[cur_offset:cur_offset + BLOCK_STRUCT['mrkl_root']].hex()
        cur_offset += BLOCK_STRUCT['mrkl_root']
        block_info['mrkl_root'] = mrkl_root
        time = blk_data[cur_offset:cur_offset + BLOCK_STRUCT['time']]
        cur_offset += BLOCK_STRUCT['time']
        block_info['time'] = time
        difficulty = blk_data[cur_offset:cur_offset + BLOCK_STRUCT['difficulty']]
        cur_offset += BLOCK_STRUCT['difficulty']
        block_info['difficulty'] = difficulty
        nonce = blk_data[cur_offset:cur_offset + BLOCK_STRUCT['nonce']]
        cur_offset += BLOCK_STRUCT['nonce']
        block_info['nonce'] = nonce
        tx_count = blk_data[cur_offset:cur_offset + BLOCK_STRUCT['tx_count']]
        cur_offset += BLOCK_STRUCT['tx_count']
        block_info['tx_count '] = tx_count
        txs = []
        
        for _ in range(int.from_bytes(tx_count, 'little')):
            tx = {}
            version = blk_data[cur_offset:cur_offset + BLOCK_STRUCT['version']]
            cur_offset += BLOCK_STRUCT['version']
            tx['version'] = version
            input_count = blk_data[cur_offset:cur_offset + BLOCK_STRUCT['input_count']]
            cur_offset += BLOCK_STRUCT['input_count']
            tx['input_count'] = input_count
            vins = []
            
            for __ in range(int.from_bytes(input_count, 'little')):
                vin = {}
                txid = blk_data[cur_offset:cur_offset + BLOCK_STRUCT['txid']]
                cur_offset += BLOCK_STRUCT['txid']
                vin['txid'] = txid
                vout = blk_data[cur_offset:cur_offset + BLOCK_STRUCT['vout']]
                cur_offset += BLOCK_STRUCT['vout']
                vin['vout'] = vout
                script_sig_size = blk_data[cur_offset:cur_offset + BLOCK_STRUCT['script_sig_size']]
                cur_offset += BLOCK_STRUCT['script_sig_size']
                vin['script_sig_size'] = script_sig_size
                script_sig = blk_data[cur_offset:cur_offset + int.from_bytes(script_sig_size, 'little')]
                cur_offset += int.from_bytes(script_sig_size, 'little')
                vin['script_sig'] = script_sig

                vins.append(vin)
            
            tx['vins'] = vins

            output_count = blk_data[cur_offset:cur_offset + BLOCK_STRUCT['output_count']]
            cur_offset += BLOCK_STRUCT['output_count']
            tx['output_count'] = output_count

            vouts = []

            for __ in range(int.from_bytes(output_count, 'little')):
                vout = {}

                value = blk_data[cur_offset:cur_offset + BLOCK_STRUCT['value']]
                cur_offset += BLOCK_STRUCT['value']
                vout['value'] = value
                script_pub_key_size = blk_data[cur_offset:cur_offset + BLOCK_STRUCT['script_pub_key_size']]
                cur_offset += BLOCK_STRUCT['script_pub_key_size']
                vout['script_pub_key_size'] = script_pub_key_size
                script_sig = blk_data[cur_offset:cur_offset + int.from_bytes(script_pub_key_size, 'little')]
                cur_offset += int.from_bytes(script_pub_key_size, 'little')
                vout['script_pub_key'] = script_sig

                vouts.append(vout)

            tx['vouts'] = vouts

            txs.append(tx)

        block_info['txs'] = txs
        
        return block_info

    def parse_nth_block_digest(self, n: int):
        return self.parse_block_digest(self.get_nth_block(n))

    def get_block_mrkl_root(self, data: bytes):
        header = self.get_block_header(data)
        cur_offset = 0
        size = 0
        for key in BLOCK_STRUCT:
            if key == 'mrkl_root':
                size = BLOCK_STRUCT[key]
                break
            else:
                cur_offset += BLOCK_STRUCT[key]
        return header[cur_offset:cur_offset + size] 

    def get_block_header(self, data: bytes):
        cur_offset = self.get_property_offset('tx_count')
        
        return data[:cur_offset]

    def get_nth_block_header(self, n: int): 
        data = self.get_nth_block(n)
        
        return self.get_block_header(data)
        
    def get_block_prev_hash(self, data: bytes):
        header = self.get_block_header(data)
        cur_offset = 0
        size = 0

        for key in BLOCK_STRUCT:
            if key == 'prev_blk_hash':
                size = BLOCK_STRUCT[key]
                break
            else:
                cur_offset += BLOCK_STRUCT[key]
        
        return header[cur_offset:cur_offset + size] 

    def get_nth_block_prev_hash(self, n: int): return Blockchain.get_block_prev_hash(Blockchain.get_nth_block(n))

    def get_vins(self, tx_data: bytes):
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

    def get_vout_offset(self, tx_data: bytes):
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

    def get_vouts(self, tx_data: bytes):
        vouts_offset = self.get_vout_offset(tx_data)
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

    def get_nth_block_txs(self, n: int):        
        
        return Blockchain.get_block_txs(Blockchain.get_nth_block(n))

    def get_block_txs(self, blk_data: bytes):
        header = self.get_block_header(blk_data)
        txs_field = blk_data[len(header):] 

        tx_count = int.from_bytes(txs_field[:BLOCK_STRUCT['tx_count']], 'little')
        cur_offset = BLOCK_STRUCT['tx_count']
        # BLOCK_STRUCT['tx_count'] = tx_count
        txs = []

        for _ in range(tx_count):
            tx = b''
            version = txs_field[cur_offset:cur_offset + BLOCK_STRUCT['version']]
            cur_offset += BLOCK_STRUCT['version']
            tx += version
            input_count = txs_field[cur_offset:cur_offset + BLOCK_STRUCT['input_count']]
            cur_offset += BLOCK_STRUCT['input_count']
            tx += input_count
            
            for __ in range(int.from_bytes(input_count, 'little')):
                vin = b''
                txid = txs_field[cur_offset:cur_offset + BLOCK_STRUCT['txid']]
                cur_offset += BLOCK_STRUCT['txid']
                vin += txid
                vout = txs_field[cur_offset:cur_offset + BLOCK_STRUCT['vout']]
                cur_offset += BLOCK_STRUCT['vout']
                vin += vout
                script_sig_size = txs_field[cur_offset:cur_offset + BLOCK_STRUCT['script_sig_size']]
                cur_offset += BLOCK_STRUCT['script_sig_size']
                vin += script_sig_size
                script_sig = txs_field[cur_offset:cur_offset + int.from_bytes(script_sig_size, 'little')]
                cur_offset += int.from_bytes(script_sig_size, 'little')
                vin += script_sig

                tx += vin
            
            output_count = txs_field[cur_offset:cur_offset + BLOCK_STRUCT['output_count']]
            cur_offset += BLOCK_STRUCT['output_count']
            tx += output_count

            for __ in range(int.from_bytes(output_count, 'little')):
                vout = b''

                value = txs_field[cur_offset:cur_offset + BLOCK_STRUCT['value']]
                cur_offset += BLOCK_STRUCT['value']
                vout += value
                script_pub_key_size = txs_field[cur_offset:cur_offset + BLOCK_STRUCT['script_pub_key_size']]
                cur_offset += BLOCK_STRUCT['script_pub_key_size']
                vout += script_pub_key_size
                script_sig = txs_field[cur_offset:cur_offset + int.from_bytes(script_pub_key_size, 'little')]
                cur_offset += int.from_bytes(script_pub_key_size, 'little')
                vout += script_sig

                tx += vout

            txs.append(tx)

        return txs
    
    def __check_block_correctness(self, index: int, blk_data: bytes, txs: List):

        if self.hash_nth_block_in_digest(index - 1) != self.get_block_prev_hash(blk_data):
            return False
        
        real_mrkl_root = self.get_block_mrkl_root(blk_data)
        got_mrkl_root = MerkleTree(txs).root

        if real_mrkl_root != got_mrkl_root:
            return False
        
        for tx in txs:
            if not self.__verify_transaction(tx):
                return False
            
        return True
    
    def __save_block(self, index: int, blk_data: bytes):
        prev_blk_data = b''
        cur_blk_file = f"{self.BLOCKS_DIR}/blk_{str(index).zfill(NUMS_IN_NAME)}.dat"
        
        #TODO: bring back transactions
        if os.path.exists(cur_blk_file):
            with open(cur_blk_file, 'rb') as f:
                prev_blk_data = f.read()

        res = len(blk_data).to_bytes(SIZE, 'little')
        res += blk_data

        with open(cur_blk_file, 'wb') as f:
            f.write(res + prev_blk_data)

    def __update_db(self, txs: List):
        for tx in txs:
            #TODO: rev file
            self.chainstate_db.update_db(tx)

    def append_block(self, index, blk_data: bytes, txs : List):
        if not self.__check_block_correctness(index, blk_data, txs):
            raise Exception('[ERROR] Block is not correct!')

        self.__save_block(index, blk_data)
        self.__update_db(txs)
        self.mempool.clear_mempool()

    def get_chain_len(self):
        # files_in_dir_len = len(os.listdir('blockchain/blocks'))
        # return math.ceil(files_in_dir_len / 2) if files_in_dir_len > 1 else files_in_dir_len
        return len(self.get_block_files())

    def get_block_files(self):
        return sorted(os.listdir(self.BLOCKS_DIR))

    def __verify_transaction(self, tx_data: bytes):
        vins = self.get_vins(tx_data)

        if len(vins) and self.chainstate_db.get_utxo(hashlib.sha256(tx_data).digest()):
            return False
        
        for vin in vins:
            txid = vin['txid']
            tx_vouts = self.chainstate_db.get_info_of_txid(txid)['vouts']
            
            if not self.confirm_sign(vin['script_sig'], tx_vouts[int.from_bytes(vin['vout'], 'little')]['script_pub_key'], txid):
                return False
        

        return True
        
    def __append_to_mempool(self, tx_data : bytes): self.mempool.add_tx(tx_data)

    def verify_chain(self):
        block_files = self.get_block_files()
        prev_blk_hash = self.hash_nth_block_in_digest(0)
        
        if len(block_files) > 1:
            for i in range(1, len(block_files)):
                cur_blk_prev_hash = self.get_nth_block_prev_hash(i)

                if prev_blk_hash != cur_blk_prev_hash:
                    return False
                    raise Exception
                else:
                    prev_blk_hash = self.hash_nth_block_in_digest(i)
            
        return True

    def add_transaction(self, vout_data: List[tuple], vin_data: List[tuple] = [], secret_key = None):

        if len(vin_data):
            coins_to_spend = sum(map(lambda value : int(value), [info_for_vout[1] for info_for_vout in vout_data]))
            txis_vout_turple = [(int(txid, 16).to_bytes(BLOCK_STRUCT['txid'], 'big'), int(vout)) for txid, vout in vin_data]
            available_coins = sum(list(map(lambda data : int.from_bytes(self.chainstate_db.get_info_of_txid(data[0])['vouts'][data[1]]['value'], 'little'), txis_vout_turple)))

            if available_coins < coins_to_spend:
                raise ValueError('[ERROR] Not enough coins on these vins!!!')        
    
        tx = Transaction(vout_data, vin_data, self, secret_key)
        tx_data = tx.tx_data

        if len(vin_data):
            self.__append_to_mempool(tx_data)

        return tx_data 

    def confirm_sign(self, script_sig, script_pub_key: bytes, message_to_sign: bytes):
        if len(script_pub_key) < 32:
            return False

        pk = ecdsa.VerifyingKey.from_string(script_pub_key, ecdsa.SECP256k1)

        return pk.verify(script_sig, message_to_sign)

