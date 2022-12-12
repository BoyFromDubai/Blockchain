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
    VOUT_STRUCT = {
        'height': 4,
        'vouts_num': 1,
        'spent': 1, 
        'value': 8, 
        'script_pub_key_size': 8,
        'script_pub_key': None, 
    }

    def __init__(self):
        self.db = plyvel.DB('chainstate/', create_if_missing=True)
        pass

    def __del__(self):
        self.db.close()

    def createVoutsStruct(self, txid, n, tx_info, wallet):
        vouts = BlkTransactions.getVouts(tx_info)
        res = Blockchain.getChainLen().to_bytes(DB.VOUT_STRUCT['height'], 'little')
        res += len(vouts).to_bytes(DB.VOUT_STRUCT['vouts_num'], 'little')
        
        for i in range(len(vouts)):
            res += (0).to_bytes(DB.VOUT_STRUCT['spent'], 'little')
            res += vouts[i]['value']
            res += vouts[i]['script_pub_key_size']
            res += vouts[i]['script_pub_key']

            if wallet.pk.to_string() == vouts[i]['script_pub_key']:
                wallet.appendUTXO(txid, i, vouts[i]['value'])

        self.db.put(txid, res)


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
        size = int.from_bytes(block[cur_offset:cur_offset + Block.SIZE], 'little')
        cur_offset += header_struct['size']
        block_info['size'] = size
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
        block_info['time'] = nonce
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
    
        # print('prev_hash:', prev_hash)

        if self.txs:
            res += MerkleTree(self.txs).root
            # print('mrkl_root: ', MerkleTree(transactions).root.hex())
        else:
            res += (0).to_bytes(self.HEADER_STRUCT['mrkl_root'], byteorder='little')

        res += int(time.time()).to_bytes(self.HEADER_STRUCT['time'], byteorder='little')
        res += self.difficulty.to_bytes(self.HEADER_STRUCT['difficulty'], byteorder='little')
        res += self.nonce.to_bytes(self.HEADER_STRUCT['nonce'], byteorder='little')

        self.header = res

        return res
    
    @staticmethod
    def getNthBlockHeader(n): 
        block = Block.getNthBlock(n)
        
        cur_offset = 0
        for key in BlkHeader.HEADER_STRUCT:
            cur_offset += BlkHeader.HEADER_STRUCT[key]
        
        return block[:cur_offset]

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
        
        return header[cur_offset:size] 

class BlkTransactions():
    TXS_STRUCT = {
        'tx_count': 1, #                        little
        'version': 4, #tx info                  little
        'input_count': 1, #tx info              little
        'txid': 32, #tx info                    little
        'vout': 4, #tx info                     little
        'script_sig_size': 8, #tx info          little
        'script_sig': None, #tx info              
        'output_count': 1, #tx info             little
        'value': 8, #tx info                    little
        'script_pub_key_size': 8, #tx info      little
        'script_pub_key': None, #tx info        
        'locktime': 4, #tx info                 little
    }

    def __init__(self, txs = []) -> None:
        self.txs = txs

    def createTxs(self):
        res = len(self.txs).to_bytes(self.TXS_STRUCT['tx_count'], byteorder='little')
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
            vin['script_sig_size'] = int.from_bytes(tx_data[cur_offset:cur_offset + BlkTransactions.TXS_STRUCT['script_sig_size']], 'little')
            script_sig = tx_data[cur_offset:cur_offset + vin['script_sig_size']]
            cur_offset += vin['script_sig_size']
            vin['script_sig'] = tx_data[cur_offset:cur_offset + BlkTransactions.TXS_STRUCT['script_sig']]
            cur_offset += script_sig
            vins.append(vin)

        return vins

    @staticmethod
    def getVoutOffset(tx_data):
        print('tx_data')
        print(tx_data)
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
        print('AAA')
        print(tx_data)
        print(tx_data[vouts_offset:])

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
        BlkTransactions.TXS_STRUCT['tx_count'] = tx_count
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

        print(txs)

        return txs

class Blockchain:
    def __init__(self, wallet):
        if not self.getChainLen():
            self.genezis_block = self.__append_block(self.__create_block(1, hashlib.sha256(pickle.dumps(17)).digest(), 1)) #TODO: change prev_hash

        self.wallet = wallet

        self.mempool_tx_size_info = 2

    def __create_block(self, nonce, prev_hash, difficulty, transactions = []):

        block = Block(nonce, prev_hash, difficulty, transactions)
        
        return block.createBlock()

    def __get_mempool(self):
        transactions = []

        with open('blockchain/mempool/mempool.dat', 'rb') as f:
            all_data = f.read()

            f.seek(0)

            while f.tell() < len(all_data):
                tx_info_len = int.from_bytes(f.read(self.mempool_tx_size_info), 'little')
                transactions.append(f.read(tx_info_len))

        return transactions
    
    def __append_block(self, blk):
        with open(f"blockchain/blocks/blk_{str(self.getChainLen()).zfill(Block.NUMS_IN_NAME)}.dat", 'wb') as f:
            f.write(blk)

    def mine_block(self, pk):
        emission = self.add_transaction([math.ceil(random.random() * 100)], [pk], sk=None, isTransaction=False)
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
        print('prev_block_hash')
        print(prev_block_hash)

        while (not(check_proof)):

            check_block = self.__create_block(nonce, prev_block_hash, num_of_zeros, transactions)

            check_block = Block(nonce, prev_block_hash, num_of_zeros, transactions)
            block_data = check_block.createBlock()

            print('BLOCK_INFO')
            print(block_data)

            header = check_block.header.header
            
            if hashlib.sha256(header).hexdigest()[:num_of_zeros] == difficulty:
                # print(difficulty)
                # print(header.hex()) 
                check_proof = True
                self.__append_block(block_data)
                self.__clear_mempool()
                # db = plyvel.DB()
                db = DB()
                # for transactions[i] in transactions:
                for i in range(len(transactions)):
                    db.createVoutsStruct(hashlib.sha256(transactions[i]).digest(), i, transactions[i], self.wallet)

                    with open('txids.txt', 'w') as f:
                        f.write(hashlib.sha256(transactions[i]).hexdigest())

                return block_data

            else:
                nonce += 1
        
        return 1

    def __clear_mempool(self):
        with open('blockchain/mempool/mempool.dat', 'w'): 
            pass

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
    

    def verifyChain(self):
        block_files = self.getBlockFiles()
        prev_blk_hash = Block.hashNthBlockInDigest(0)
        print(prev_blk_hash)
        
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
                    print(vouts)

                    for i in range(len(vouts)):

                        if vouts[i]['script_pub_key'].hex() == self.wallet.sk.get_verifying_key().to_string().hex():
                            self.wallet.appendUTXO(hashlib.sha256(tx).digest(), i, vouts[i]['value'])


                    print(self.wallet.utxos)
                    

                    # for i in range(len(tx['vouts'])):
                    #     print(self.wallet.sk.get_verifying_key().to_string().hex())
                    #     print(tx['vouts'][i]['script_pub_key'])
                    #     if tx['vouts'][i]['script_pub_key'] == self.wallet.sk.get_verifying_key().to_string().hex():
                    #         print(self.wallet.utxos)
                    #         self.wallet.appendUTXO(hashlib.sha256(tx).digest(), i, tx['vouts'][i]['value'])

            
            return True

    def add_transaction(self, value, addresses, sk, txid = [], vout_num = [], isTransaction = True):
        version = (0).to_bytes(BlkTransactions.TXS_STRUCT['version'], "little")
        tx_data = version
        inputs_num = len(txid).to_bytes(BlkTransactions.TXS_STRUCT['input_count'], "little")
        tx_data += inputs_num
        
        for i in range(len(txid)):
            tx_data += self.__create_vin(txid[i], int(vout_num[i]), sk)

        tx_data += len(addresses).to_bytes(1, "big") #outputs num

        for i in range(len(addresses)):
            tx_data += self.__create_vout(int(value[i]), addresses[i])
        
        if isTransaction:
            self.__append_to_mempool(tx_data)
        
        print(tx_data)
        
        return tx_data

    def __append_to_mempool(self, tx_bytes):
        if not os.path.isdir('blockchain/mempool'): 
            os.mkdir('blockchain/mempool')
        
        with open('blockchain/mempool/mempool.dat', 'ab') as f:
            f.write(len(tx_bytes).to_bytes(self.mempool_tx_size_info, 'little'))
            f.write(tx_bytes)

        # with open('blockchain/mempool/mempool.dat', 'wb') as f:
        #     pass
            
    def get_chain(self): return data.get_chain()

    def __create_vin(self, txid, vout_num, sk):
        if not txid or not vout_num:
            return None
        vin_data = int(txid, 16).to_bytes(BlkTransactions.TXS_STRUCT['txid'], 'little')
        vin_data += vout_num.to_bytes(BlkTransactions.TXS_STRUCT['vout'], "little")

        scriptSig = sk.sign(int(txid, 16).to_bytes(BlkTransactions.TXS_STRUCT['txid'], 'little'))
        vin_data += len(scriptSig).to_bytes(BlkTransactions.TXS_STRUCT['script_sig_size'], "little") #ScriptSig size
        vin_data += scriptSig #ScriptSig

        return vin_data

    def __create_vout(self, value, address):

        vout_data = int(value).to_bytes(BlkTransactions.TXS_STRUCT['value'], "little")

        script_pub_key = int(address, 16).to_bytes(math.ceil(len(address) / 2), 'big') 
        vout_data += len(script_pub_key).to_bytes(BlkTransactions.TXS_STRUCT['script_sig_size'], "little") #ScriptPubKey size
        vout_data += script_pub_key #ScriptPubKey

        return vout_data