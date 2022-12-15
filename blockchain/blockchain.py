import datetime
import hashlib
import random
import math
from blockchain.save_data import data
from blockchain.mrkl_tree import MerkleTree
import pickle
import os
import time
import ecdsa
import plyvel
# from leveldb.database_code import *


class DB():
    VOUTS_STRUCT = {
        'height': 4,
        'vouts_num': 1,
        'spent': 1, 
        'value': 8, 
        'script_pub_key_size': 8,
        'script_pub_key': None, 
    }

    def __init__(self):
        self.db = plyvel.DB('chainstate/', create_if_missing=True)

    def __del__(self):
        self.db.close()

    def __create_utxo_struct(self, tx_info):
        vouts = BlkTransactions.getVouts(tx_info)

        res = Blockchain.getChainLen().to_bytes(DB.VOUTS_STRUCT['height'], 'little')
        res += len(vouts).to_bytes(DB.VOUTS_STRUCT['vouts_num'], 'little')
        
        for i in range(len(vouts)):
            res += (0).to_bytes(DB.VOUTS_STRUCT['spent'], 'little')
            res += vouts[i]['value']
            res += vouts[i]['script_pub_key_size']
            res += vouts[i]['script_pub_key']

        return res
    
    def showDB(self):
        arr = []
        for key, value in self.db:
            # print('VALUE')
            # print(value)
            arr.append((key.hex(), self.__parse_tx_utxos(value)))

        return arr

    def __parse_tx_utxos(self, tx_utxos_digest):
        cur_offset = 0
        utxos_dict = {}
        utxos_dict['hight'] = int.from_bytes(tx_utxos_digest[cur_offset:cur_offset + self.VOUTS_STRUCT['height']], 'little')
        cur_offset += self.VOUTS_STRUCT['height']
        utxos_dict['vouts_num'] = int.from_bytes(tx_utxos_digest[cur_offset:cur_offset + self.VOUTS_STRUCT['vouts_num']], 'little')
        cur_offset += self.VOUTS_STRUCT['vouts_num']

        utxos = []

        for _ in range(utxos_dict['vouts_num']):
            utxo = {}

            utxo['spent'] = int.from_bytes(tx_utxos_digest[cur_offset:cur_offset + self.VOUTS_STRUCT['spent']], 'little')
            cur_offset += self.VOUTS_STRUCT['spent']
            utxo['value'] = int.from_bytes(tx_utxos_digest[cur_offset:cur_offset + self.VOUTS_STRUCT['value']], 'little')
            cur_offset += self.VOUTS_STRUCT['value']
            utxo['script_pub_key_size'] = int.from_bytes(tx_utxos_digest[cur_offset:cur_offset + self.VOUTS_STRUCT['script_pub_key_size']], 'little')
            cur_offset += self.VOUTS_STRUCT['script_pub_key_size']
            utxo['script_pub_key'] = tx_utxos_digest[cur_offset:cur_offset + utxo['script_pub_key_size']].hex()
            cur_offset += utxo['script_pub_key_size']

            utxos.append(utxo)

        print(utxos)
        utxos_dict['vouts'] = utxos

        return utxos_dict

    def __change_spent_field(self, tx_utxos_digest, vout):
        cur_offset = 0

        print('SPENDING STARTED!!!')
        print(vout)
        
        res = tx_utxos_digest[cur_offset:cur_offset + self.VOUTS_STRUCT['height']]
        cur_offset += self.VOUTS_STRUCT['height']
        vouts_num = tx_utxos_digest[cur_offset:cur_offset + self.VOUTS_STRUCT['vouts_num']] 
        res += vouts_num
        cur_offset += self.VOUTS_STRUCT['vouts_num']

        delete_tx = True 

        for i in range(int.from_bytes(vouts_num, 'little')):
            spent = tx_utxos_digest[cur_offset:cur_offset + self.VOUTS_STRUCT['spent']]

            if i == vout:
                if not int.from_bytes(spent, 'little'):
                    print('SPENT SUCCESSFULLY')
                    res += (1).to_bytes(self.VOUTS_STRUCT['spent'], 'little') 
                else:
                    print('CANT\' BE SPENT')
                    return False
            else:
                if not int.from_bytes(spent, 'little'):
                    delete_tx = False

                res += spent

            cur_offset += self.VOUTS_STRUCT['spent']
            pub_key_size = tx_utxos_digest[cur_offset:cur_offset + self.VOUTS_STRUCT['script_pub_key_size']] 
            res += pub_key_size
            cur_offset += self.VOUTS_STRUCT['script_pub_key_size']
            res += tx_utxos_digest[cur_offset:cur_offset + int.from_bytes(pub_key_size, 'little')]
            cur_offset += int.from_bytes(pub_key_size, 'little')

        return res, delete_tx


    def updateDB(self, tx_info):
        
        vins = BlkTransactions.getVins(tx_info)
        print('For exception!!!!!!!!!!!')
        print(vins)
        for vin in vins:
            txid = vin['txid']
            vout = int.from_bytes(vin['vout'], 'little')
            self.__spend_utxo(txid, vout)

        tx_utxos = self.__create_utxo_struct(tx_info)
        
        self.db.put(hashlib.sha256(tx_info).digest(), tx_utxos)

    def __spend_utxo(self, txid, vout):
        tx_utxos = self.db.get(txid)

        updated_tx, delete_tx = self.__change_spent_field(tx_utxos, vout)      

        if not updated_tx:
            raise ValueError('[ERROR] This vout if already spend!!!')
        else:
            self.db.delete(txid)

            if not delete_tx:
                self.db.put(txid, updated_tx)

    def showAll(self):
        for key, value in self.db:
            print(key)

    def getInfoOfTxid(self, txid):
        info_to_txid = self.db.get(txid)

        if not info_to_txid:
            raise ValueError('[ERROR] No such TXID in chain!!!')
        
        else:
            info_for_txid = {}
            cur_offset = 0

            info_for_txid['height'] = info_to_txid[cur_offset:cur_offset + self.VOUTS_STRUCT['height']]
            cur_offset += self.VOUTS_STRUCT['height']
            info_for_txid['vouts_num'] = info_to_txid[cur_offset:cur_offset + self.VOUTS_STRUCT['vouts_num']]
            cur_offset += self.VOUTS_STRUCT['vouts_num']

            vouts = []
            for _ in range(int.from_bytes(info_for_txid['vouts_num'], 'little')):
                vout = {}

                vout['spent'] = info_to_txid[cur_offset:cur_offset + self.VOUTS_STRUCT['spent']]
                cur_offset += self.VOUTS_STRUCT['spent']
                vout['value'] = info_to_txid[cur_offset:cur_offset + self.VOUTS_STRUCT['value']]
                cur_offset += self.VOUTS_STRUCT['value']
                
                vout['script_pub_key_size'] = info_to_txid[cur_offset:cur_offset + self.VOUTS_STRUCT['script_pub_key_size']]
                cur_offset += self.VOUTS_STRUCT['script_pub_key_size']
                vout['script_pub_key'] = info_to_txid[cur_offset:cur_offset + int.from_bytes(vout['script_pub_key_size'], 'little')]
                cur_offset += int.from_bytes(vout['script_pub_key_size'], 'little')

                vouts.append(vout)

            info_for_txid['vouts'] = vouts

            return info_for_txid

class Block():
    SIZE = 4
    NUMS_IN_NAME = 4

    def __init__(self, nonce, prev_hash, difficulty, txs = []) -> None:
        self.header = BlkHeader(nonce, prev_hash, difficulty, txs)
        self.txs = BlkTransactions(txs)

    def createBlock(self):
        res = self.header.createHeader() + self.txs.createTxs()
        size = len(res).to_bytes(self.SIZE, byteorder='little')

        return size + res

    @staticmethod
    def getNthBlock(n):
        with open(f'blockchain/blocks/blk_{str(n).zfill(Block.NUMS_IN_NAME)}.dat', 'rb') as f:
            return f.read()[Block.SIZE:]

    @staticmethod
    def hashNthBlockInDigest(n):
        return hashlib.sha256(BlkHeader.getNthBlockHeader(n)).digest()

    @staticmethod
    def hashNthBlockInHexdigest(n):
        return hashlib.sha256(BlkHeader.getNthBlockHeader(n)).hexdigest()

    @staticmethod
    def hashLastBlockInDigest():
        return hashlib.sha256(BlkHeader.getNthBlockHeader(Blockchain.getChainLen() - 1)).digest()

    @staticmethod
    def hashLastBlockInHexdigest():
        return hashlib.sha256(BlkHeader.getNthBlockHeader(Blockchain.getChainLen() - 1)).hexdigest()

    @staticmethod
    def parseBlock(n):
        block = Block.getNthBlock(n)
        header_struct = BlkHeader.HEADER_STRUCT
        txs_struct = BlkTransactions.TXS_STRUCT

        block_info = {}

        cur_offset = 0
        prev_blk_hash = block[cur_offset:cur_offset + header_struct['prev_blk_hash']].hex()
        cur_offset += header_struct['prev_blk_hash']
        block_info['prev_blk_hash'] = prev_blk_hash
        mrkl_root = block[cur_offset:cur_offset + header_struct['mrkl_root']].hex()
        cur_offset += header_struct['mrkl_root']
        block_info['mrkl_root'] = mrkl_root
        time = int.from_bytes(block[cur_offset:cur_offset + header_struct['time']], 'little')
        cur_offset += header_struct['time']
        block_info['time'] = time
        difficulty = int.from_bytes(block[cur_offset:cur_offset + header_struct['difficulty']], 'little')
        cur_offset += header_struct['difficulty']
        block_info['difficulty'] = difficulty
        nonce = int.from_bytes(block[cur_offset:cur_offset + header_struct['nonce']], 'little')
        cur_offset += header_struct['nonce']
        block_info['nonce'] = nonce
        tx_count = int.from_bytes(block[cur_offset:cur_offset + txs_struct['tx_count']], 'little')
        cur_offset += txs_struct['tx_count']
        block_info['tx_count '] = tx_count
        txs = []
        
        for _ in range(tx_count):
            tx = {}
            version = int.from_bytes(block[cur_offset:cur_offset + txs_struct['version']], 'little')
            cur_offset += txs_struct['version']
            tx['version'] = version
            input_count = int.from_bytes(block[cur_offset:cur_offset + txs_struct['input_count']], 'little')
            cur_offset += txs_struct['input_count']
            tx['input_count'] = input_count
            vins = []
            
            for __ in range(input_count):
                vin = {}
                txid = hex(int.from_bytes(block[cur_offset:cur_offset + txs_struct['txid']], 'little'))[2:]
                cur_offset += txs_struct['txid']
                vin['txid'] = txid
                vout = int.from_bytes(block[cur_offset:cur_offset + txs_struct['vout']], 'little')
                cur_offset += txs_struct['vout']
                vin['vout'] = vout
                script_sig_size = int.from_bytes(block[cur_offset:cur_offset + txs_struct['script_sig_size']], 'little')
                cur_offset += BlkTransactions.TXS_STRUCT['script_sig_size']
                vin['script_sig_size'] = script_sig_size
                script_sig = block[cur_offset:cur_offset + script_sig_size].hex()
                cur_offset += script_sig_size
                vin['script_sig'] = script_sig

                vins.append(vin)
            
            tx['vins'] = vins

            output_count = int.from_bytes(block[cur_offset:cur_offset + txs_struct['output_count']], 'little')
            cur_offset += txs_struct['output_count']
            tx['output_count'] = output_count

            vouts = []

            for __ in range(output_count):
                vout = {}

                value = int.from_bytes(block[cur_offset:cur_offset + txs_struct['value']], 'little')
                cur_offset += txs_struct['value']
                vout['value'] = value
                script_pub_key_size = int.from_bytes(block[cur_offset:cur_offset + txs_struct['script_pub_key_size']], 'little')
                cur_offset += txs_struct['script_pub_key_size']
                vout['script_pub_key_size'] = script_pub_key_size
                script_sig = block[cur_offset:cur_offset + script_pub_key_size].hex()
                cur_offset += script_pub_key_size
                vout['script_pub_key'] = script_sig

                vouts.append(vout)

            tx['vouts'] = vouts

            txs.append(tx)

        block_info['txs'] = txs
        
        return block_info


    @staticmethod
    def parseBlockDigest(n):
        block = Block.getNthBlock(n)
        header_struct = BlkHeader.HEADER_STRUCT
        txs_struct = BlkTransactions.TXS_STRUCT

        block_info = {}

        cur_offset = 0
        prev_blk_hash = block[cur_offset:cur_offset + header_struct['prev_blk_hash']]
        cur_offset += header_struct['prev_blk_hash']
        block_info['prev_blk_hash'] = prev_blk_hash
        mrkl_root = block[cur_offset:cur_offset + header_struct['mrkl_root']].hex()
        cur_offset += header_struct['mrkl_root']
        block_info['mrkl_root'] = mrkl_root
        time = block[cur_offset:cur_offset + header_struct['time']]
        cur_offset += header_struct['time']
        block_info['time'] = time
        difficulty = block[cur_offset:cur_offset + header_struct['difficulty']]
        cur_offset += header_struct['difficulty']
        block_info['difficulty'] = difficulty
        nonce = block[cur_offset:cur_offset + header_struct['nonce']]
        cur_offset += header_struct['nonce']
        block_info['nonce'] = nonce
        tx_count = block[cur_offset:cur_offset + txs_struct['tx_count']]
        cur_offset += txs_struct['tx_count']
        block_info['tx_count '] = tx_count
        txs = []
        
        for _ in range(int.from_bytes(tx_count, 'little')):
            tx = {}
            version = block[cur_offset:cur_offset + txs_struct['version']]
            cur_offset += txs_struct['version']
            tx['version'] = version
            input_count = block[cur_offset:cur_offset + txs_struct['input_count']]
            cur_offset += txs_struct['input_count']
            tx['input_count'] = input_count
            vins = []
            
            for __ in range(int.from_bytes(input_count, 'little')):
                vin = {}
                txid = block[cur_offset:cur_offset + txs_struct['txid']]
                cur_offset += txs_struct['txid']
                vin['txid'] = txid
                vout = block[cur_offset:cur_offset + txs_struct['vout']]
                cur_offset += txs_struct['vout']
                vin['vout'] = vout
                script_sig_size = block[cur_offset:cur_offset + txs_struct['script_sig_size']]
                cur_offset += BlkTransactions.TXS_STRUCT['script_sig_size']
                vin['script_sig_size'] = script_sig_size
                script_sig = block[cur_offset:cur_offset + int.from_bytes(script_sig_size, 'little')]
                cur_offset += int.from_bytes(script_sig_size, 'little')
                vin['script_sig'] = script_sig

                vins.append(vin)
            
            tx['vins'] = vins

            output_count = block[cur_offset:cur_offset + txs_struct['output_count']]
            cur_offset += txs_struct['output_count']
            tx['output_count'] = output_count

            vouts = []

            for __ in range(int.from_bytes(output_count, 'little')):
                vout = {}

                value = block[cur_offset:cur_offset + txs_struct['value']]
                cur_offset += txs_struct['value']
                vout['value'] = value
                script_pub_key_size = block[cur_offset:cur_offset + txs_struct['script_pub_key_size']]
                cur_offset += txs_struct['script_pub_key_size']
                vout['script_pub_key_size'] = script_pub_key_size
                script_sig = block[cur_offset:cur_offset + int.from_bytes(script_pub_key_size, 'little')]
                cur_offset += int.from_bytes(script_pub_key_size, 'little')
                vout['script_pub_key'] = script_sig

                vouts.append(vout)

            tx['vouts'] = vouts

            txs.append(tx)

        block_info['txs'] = txs
        
        return block_info



class BlkHeader():
    HEADER_STRUCT = {
        'prev_blk_hash': 32, # header info      little
        'mrkl_root': 32, # header info          little
        'time': 4, # header info                little
        'difficulty': 4, # header info          little
        'nonce': 4, # header info               little
    }

    def __init__(self, nonce, prev_hash, difficulty, txs):
        self.nonce = nonce
        self.prev_hash = prev_hash
        self.difficulty = difficulty
        self.txs = txs

        self.header = None

    def createHeader(self) -> bytes:
    
        res = self.prev_hash
    
        if self.txs:
            res += MerkleTree(self.txs).root
        else:
            res += (0).to_bytes(self.HEADER_STRUCT['mrkl_root'], byteorder='little')

        res += int(time.time()).to_bytes(self.HEADER_STRUCT['time'], byteorder='little')
        res += self.difficulty.to_bytes(self.HEADER_STRUCT['difficulty'], byteorder='little')
        res += self.nonce.to_bytes(self.HEADER_STRUCT['nonce'], byteorder='little')

        self.header = res

        return res

    @staticmethod
    def getBlockMrklRoot(data):
        header = BlkHeader.getBlockHeader(data)
        cur_offset = 0
        size = 0
        for key in BlkHeader.HEADER_STRUCT:
            if key == 'mrkl_root':
                size = BlkHeader.HEADER_STRUCT[key]
                break
            else:
                cur_offset += BlkHeader.HEADER_STRUCT[key]
        return header[cur_offset:cur_offset + size] 
    
    @staticmethod
    def getBlockHeader(data):
        cur_offset = 0
        for key in BlkHeader.HEADER_STRUCT:
            cur_offset += BlkHeader.HEADER_STRUCT[key]
        
        return data[:cur_offset]

    @staticmethod
    def getNthBlockHeader(n): 
        data = Block.getNthBlock(n)
        
        return BlkHeader.getBlockHeader(data)
        

    @staticmethod
    def getNthBlockPrevHash(n):
        header = BlkHeader.getNthBlockHeader(n)
        cur_offset = 0
        size = 0
        for key in BlkHeader.HEADER_STRUCT:
            if key == 'prev_blk_hash':
                size = BlkHeader.HEADER_STRUCT[key]
                break
            else:
                cur_offset += BlkHeader.HEADER_STRUCT[key]
        
        return header[cur_offset:cur_offset + size] 

class BlkTransactions():
    TXS_STRUCT = {
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

    def __init__(self, txs = []) -> None:
        self.txs = txs

    def createTxs(self):
        res = len(self.txs).to_bytes(self.TXS_STRUCT['tx_count'], byteorder='big')
        for tx in self.txs:
            res += tx


        return res

    @staticmethod
    def getVins(tx_data):
        vins = []

        cur_offset = BlkTransactions.TXS_STRUCT['version']
        vins_field_len = BlkTransactions.TXS_STRUCT['input_count']
        vins_num = int.from_bytes(tx_data[cur_offset:cur_offset + vins_field_len], 'little')
        cur_offset += vins_field_len

        for _ in range(vins_num):
            vin = {}
            vin['txid'] = tx_data[cur_offset:cur_offset + BlkTransactions.TXS_STRUCT['txid']]
            cur_offset += BlkTransactions.TXS_STRUCT['txid']
            vin['vout'] = tx_data[cur_offset:cur_offset + BlkTransactions.TXS_STRUCT['vout']]
            cur_offset += BlkTransactions.TXS_STRUCT['vout']
            vin['script_sig_size'] = tx_data[cur_offset:cur_offset + BlkTransactions.TXS_STRUCT['script_sig_size']]
            # script_sig = tx_data[cur_offset:cur_offset + vin['script_sig_size']]
            cur_offset += BlkTransactions.TXS_STRUCT['script_sig_size']
            vin['script_sig'] = tx_data[cur_offset:cur_offset + int.from_bytes(vin['script_sig_size'], 'little')]
            cur_offset += int.from_bytes(vin['script_sig_size'], 'little')
            vins.append(vin)

        return vins

    @staticmethod
    def getVoutOffset(tx_data):
        cur_offset = BlkTransactions.TXS_STRUCT['version']
        vins_num = int.from_bytes(tx_data[cur_offset:cur_offset + BlkTransactions.TXS_STRUCT['input_count']], 'little')
        cur_offset += BlkTransactions.TXS_STRUCT['input_count']

        for _ in range(vins_num):
            cur_offset += BlkTransactions.TXS_STRUCT['txid']
            cur_offset += BlkTransactions.TXS_STRUCT['vout']
            script_sig_size = int.from_bytes(tx_data[cur_offset:cur_offset + BlkTransactions.TXS_STRUCT['script_sig_size']], 'little')
            cur_offset += BlkTransactions.TXS_STRUCT['script_sig_size']
            cur_offset += script_sig_size

        return cur_offset

    @staticmethod
    def getVouts(tx_data):
        vouts_offset = BlkTransactions.getVoutOffset(tx_data)

        vouts_info = tx_data[vouts_offset:]
        cur_offset = 0
        vouts_field_len = BlkTransactions.TXS_STRUCT['output_count']
        vouts_num = int.from_bytes(vouts_info[cur_offset:cur_offset + vouts_field_len], 'little')
        cur_offset += vouts_field_len
        vouts = []

        for _ in range(vouts_num):
            vout = {}
            value = vouts_info[cur_offset:cur_offset + BlkTransactions.TXS_STRUCT['value']]
            cur_offset += BlkTransactions.TXS_STRUCT['value']
            vout['value'] = value
            script_pub_key_size = vouts_info[cur_offset:cur_offset + BlkTransactions.TXS_STRUCT['script_pub_key_size']]
            cur_offset += BlkTransactions.TXS_STRUCT['script_pub_key_size']
            vout['script_pub_key_size'] = script_pub_key_size
            script_sig = vouts_info[cur_offset:cur_offset + int.from_bytes(script_pub_key_size, 'little')]
            cur_offset += int.from_bytes(script_pub_key_size, 'little')
            vout['script_pub_key'] = script_sig

            vouts.append(vout)
        
        return vouts

    @staticmethod
    def getNthBlockTxs(n):
        block = Block.getNthBlock(n)
        header = BlkHeader.getNthBlockHeader(n)

        txs_data = block[len(header):] 
        
        return BlkTransactions.getBlockTxs(txs_data)

    @staticmethod
    def getBlockTxs(data):

        tx_count = int.from_bytes(data[:BlkTransactions.TXS_STRUCT['tx_count']], 'little')
        cur_offset = BlkTransactions.TXS_STRUCT['tx_count']
        # BlkTransactions.TXS_STRUCT['tx_count'] = tx_count
        txs = []
    
        for _ in range(tx_count):
            tx = b''
            version = data[cur_offset:cur_offset + BlkTransactions.TXS_STRUCT['version']]
            cur_offset += BlkTransactions.TXS_STRUCT['version']
            tx += version
            input_count = data[cur_offset:cur_offset + BlkTransactions.TXS_STRUCT['input_count']]
            cur_offset += BlkTransactions.TXS_STRUCT['input_count']
            tx += input_count
            
            for __ in range(int.from_bytes(input_count, 'little')):
                vin = b''
                txid = data[cur_offset:cur_offset + BlkTransactions.TXS_STRUCT['txid']]
                cur_offset += BlkTransactions.TXS_STRUCT['txid']
                vin += txid
                vout = data[cur_offset:cur_offset + BlkTransactions.TXS_STRUCT['vout']]
                cur_offset += BlkTransactions.TXS_STRUCT['vout']
                vin += vout
                script_sig_size = data[cur_offset:cur_offset + BlkTransactions.TXS_STRUCT['script_sig_size']]
                cur_offset += BlkTransactions.TXS_STRUCT['script_sig_size']
                vin += script_sig_size
                script_sig = data[cur_offset:cur_offset + int.from_bytes(script_sig_size, 'little')]
                cur_offset += int.from_bytes(script_sig_size, 'little')
                vin += script_sig

                tx += vin
            
            output_count = data[cur_offset:cur_offset + BlkTransactions.TXS_STRUCT['output_count']]
            cur_offset += BlkTransactions.TXS_STRUCT['output_count']
            tx += output_count

            for __ in range(int.from_bytes(output_count, 'little')):
                vout = b''

                value = data[cur_offset:cur_offset + BlkTransactions.TXS_STRUCT['value']]
                cur_offset += BlkTransactions.TXS_STRUCT['value']
                vout += value
                script_pub_key_size = data[cur_offset:cur_offset + BlkTransactions.TXS_STRUCT['script_pub_key_size']]
                cur_offset += BlkTransactions.TXS_STRUCT['script_pub_key_size']
                vout += script_pub_key_size
                script_sig = data[cur_offset:cur_offset + int.from_bytes(script_pub_key_size, 'little')]
                cur_offset += int.from_bytes(script_pub_key_size, 'little')
                vout += script_sig

                tx += vout

            txs.append(tx)

        return txs

class Blockchain:
    
    MEMPOOL_TX_SIZE_INFO = 2

    def __init__(self, wallet):
        if not self.getChainLen():
            self.__append_block(self.__create_block(1, hashlib.sha256(pickle.dumps(17)).digest(), 1)) #TODO: change prev_hash

        self.wallet = wallet
        self.db = DB()

    def __create_block(self, nonce, prev_hash, difficulty, transactions = []):

        block = Block(nonce, prev_hash, difficulty, transactions)
        
        return block.createBlock()

    def __get_mempool(self):
        transactions = []

        with open('blockchain/mempool/mempool.dat', 'rb') as f:
            all_data = f.read()

            f.seek(0)

            while f.tell() < len(all_data):
                tx_info_len = int.from_bytes(f.read(self.MEMPOOL_TX_SIZE_INFO), 'little')
                transactions.append(f.read(tx_info_len))

        return transactions
    
    def __append_block(self, blk):
        with open(f"blockchain/blocks/blk_{str(self.getChainLen()).zfill(Block.NUMS_IN_NAME)}.dat", 'wb') as f:
            f.write(blk)

    def mineBlock(self, pk):
        emission = self.addTransaction([math.ceil(random.random() * 100)], [pk], isTransaction=False)
        transactions = [emission]
        # mempool = self.__get_mempool()[1:]
        mempool = self.__get_mempool()

        for tx in mempool: 
            transactions.append(tx)

        nonce = 1
        check_proof = False
        num_of_zeros = 1
        difficulty = ''.zfill(num_of_zeros)
            
        prev_block_hash = Block.hashLastBlockInDigest()

        while (not(check_proof)):

            check_block = self.__create_block(nonce, prev_block_hash, num_of_zeros, transactions)

            check_block = Block(nonce, prev_block_hash, num_of_zeros, transactions)
            block_data = check_block.createBlock()

            header = check_block.header.header
            
            if hashlib.sha256(header).hexdigest()[:num_of_zeros] == difficulty:
                check_proof = True
                self.__append_block(block_data)
                self.__clear_mempool()

                for tx in transactions:
                    self.appendVoutsToDb(tx)

                return block_data[Block.SIZE:]

            else:
                nonce += 1
        
        return 1

    def __clear_mempool(self):
        with open('blockchain/mempool/mempool.dat', 'wb'): 
            pass

    def appendVoutsToDb(self, tx):
        self.db.updateDB(tx)

        with open('wallet/txids.txt', 'w') as f:
            f.write(hashlib.sha256(tx).hexdigest())

    @staticmethod
    def getChainLen():
        if os.path.exists('blockchain/blocks'):
            return len(os.listdir('blockchain/blocks')) 
        else:
            os.mkdir('blockchain/blocks')
            return 0

    @staticmethod
    def getBlockFiles():
        return sorted(os.listdir('blockchain/blocks'))

    def verifyTransaction(self, tx_data):
        vins = BlkTransactions.getVins(tx_data)

        for vin in vins:
            txid = vin['txid']

            tx_vouts = self.db.getInfoOfTxid(txid)['vouts']
            print('tx_vouts')
            print(tx_vouts)
            # if vout_num > len(tx_vouts) - 1:
            #     raise ValueError('[ERROR] Not enough vouts in tx!!!')

        print('vins')
        print(vins)
        ## TODO: tx verification

        Blockchain.appendToMempool(tx_data)     

    def getNewBlockFromPeer(self, blk_data):
        print('BLOCK DATA')
        print(blk_data)

        txs = BlkTransactions.getBlockTxs(blk_data[len(BlkHeader.getBlockHeader(blk_data)):])
        print(txs)
        real_mrkl_root = BlkHeader.getBlockMrklRoot(blk_data)
        got_mrkl_root = MerkleTree(txs).root

        if real_mrkl_root == got_mrkl_root:
            cur_len = Blockchain.getChainLen()

            with open(f'blockchain/blocks/blk_{str(cur_len).zfill(4)}.dat', 'wb') as f:
                f.write(len(blk_data).to_bytes(Block.SIZE, 'little') + blk_data)
            
            for tx in txs:
                self.db.updateDB(tx)

        else:
            print('[ERROR]: New Block was falsified')
   

    def verifyChain(self):
        block_files = self.getBlockFiles()
        prev_blk_hash = Block.hashNthBlockInDigest(0)
        
        if len(block_files) > 1:
            for i in range(1, len(block_files)):
                cur_blk_prev_hash = BlkHeader.getNthBlockPrevHash(i)

                if prev_blk_hash != cur_blk_prev_hash:
                    return False
                else:
                    prev_blk_hash = Block.hashNthBlockInDigest(i)

                block_txs = BlkTransactions.getNthBlockTxs(i)

                for tx in block_txs:
                    vouts = BlkTransactions.getVouts(tx)

                    for i in range(len(vouts)):

                        if vouts[i]['script_pub_key'].hex() == self.wallet.sk.get_verifying_key().to_string().hex():
                            self.wallet.appendUTXO(hashlib.sha256(tx).digest(), i, vouts[i]['value'])
            
        return True

    def addTransaction(self, value, addresses, txid = [], vout_num = [], isTransaction = True):
        version = (0).to_bytes(BlkTransactions.TXS_STRUCT['version'], "little")
        tx_data = version
        inputs_num = len(txid).to_bytes(BlkTransactions.TXS_STRUCT['input_count'], "little")
        tx_data += inputs_num
        
        for i in range(len(txid)):
            tx_data += self.__create_vin(txid[i], int(vout_num[i]))

        tx_data += len(addresses).to_bytes(1, "little") #outputs num

        for i in range(len(addresses)):
            tx_data += self.__create_vout(int(value[i]), addresses[i])
        
        if isTransaction:
            self.appendToMempool(tx_data)
                
        return tx_data
        
    @staticmethod
    def appendToMempool(tx_bytes):
        if not os.path.isdir('blockchain/mempool'): 
            os.mkdir('blockchain/mempool')
        
        with open('blockchain/mempool/mempool.dat', 'ab') as f:
            f.write(len(tx_bytes).to_bytes(Blockchain.MEMPOOL_TX_SIZE_INFO, 'little'))
            f.write(tx_bytes)
            
    def get_chain(self): return data.get_chain()

    def __create_vin(self, txid, vout_num):
        txid = int(txid, 16).to_bytes(BlkTransactions.TXS_STRUCT['txid'], 'big')

        tx_vouts = self.db.getInfoOfTxid(txid)['vouts']

        if vout_num > len(tx_vouts) - 1:
            raise ValueError('[ERROR] Not enough vouts in tx!!!')

        else:
            vout = tx_vouts[vout_num]
            print(vout)

            if int.from_bytes(vout['spent'], 'little'):
                raise ValueError('[ERROR] Vout is already spent!!!')
            else:
                script_pub_key = vout['script_pub_key'] 
                
                vin_data = txid 
                vin_data += vout_num.to_bytes(BlkTransactions.TXS_STRUCT['vout'], "little")

                message_to_sign = txid
                scriptSig = self.wallet.sk.sign(message_to_sign)
                
                if not self.confirmSign(scriptSig, script_pub_key, message_to_sign):
                    raise ValueError('[ERROR] Signature failed!')

                vin_data += len(scriptSig).to_bytes(BlkTransactions.TXS_STRUCT['script_sig_size'], "little") #ScriptSig size
                vin_data += scriptSig #ScriptSig

                return vin_data

    def confirmSign(self, scriptSig, scriptPubKey, message_to_sign):
        if len(scriptPubKey) < 32:
            return False

        pk = ecdsa.VerifyingKey.from_string(scriptPubKey, ecdsa.SECP256k1)

        return pk.verify(scriptSig, message_to_sign)

    def __create_vout(self, value, address):

        vout_data = int(value).to_bytes(BlkTransactions.TXS_STRUCT['value'], "little")

        script_pub_key = int(address, 16).to_bytes(math.ceil(len(address) / 2), 'big') 
        vout_data += len(script_pub_key).to_bytes(BlkTransactions.TXS_STRUCT['script_sig_size'], "little") #ScriptPubKey size
        vout_data += script_pub_key #ScriptPubKey

        return vout_data