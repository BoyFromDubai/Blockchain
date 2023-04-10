from .miner import Miner
from .network_node import NetworkNode
from .wallet import Wallet
from ..blockchain import Blockchain

import json

class Node:
    def __init__(self) -> None:
        self.__blockchain = Blockchain()
        self.__wallet = Wallet(self.__blockchain)
        self.__miner = Miner(self.__blockchain, self.__wallet.pk.to_string().hex())
        self.__network_node = NetworkNode(self.__blockchain)
        self.__network_node.start()

        self.__verify_chain()

    def __update_utxos(func):
        def wrapper(*args, **kwargs):
            blk_data = func(*args, **kwargs)
            txs = args[0].__blockchain.get_block_txs(blk_data)

            args[0].__wallet.update_utxos(txs)

            return blk_data

        return wrapper

    def append_to_vins(self, vin: tuple): self.__wallet.append_to_vins(vin)

    def append_to_vouts(self, vout: tuple): self.__wallet.append_to_vouts(vout)

    def create_tx(self):
        try:
            vins = self.__wallet.get_vins()
            vouts = self.__wallet.get_vouts()
            tx_data = self.__blockchain.add_transaction(vouts, vins, self.__wallet.sk)
            self.__network_node.new_tx_msg(tx_data)
                
            return tx_data
        
        except Exception as e:
            return e
        
        finally:
            self.__wallet.clear_vins()
            self.__wallet.clear_vouts()
    
    def set_bind_server(self, ip: str, port: str): return self.__network_node.set_bind_server(ip, port)

    def get_ip(self): return self.__network_node.ip

    def get_peers(self): return self.__network_node.get_peers()
    
    def get_chain_len(self): return self.__blockchain.get_chain_len()

    def get_db_utxos(self): return json.dumps(self.__blockchain.chainstate_db.get_utxos(), indent=2)

    def get_my_utxos(self): return self.__wallet.get_utxos()

    # @__update_utxos
    def mine_block(self):
        blk_info = self.__miner.mine_block() 
        self.__network_node.new_block_msg(blk_info)
        
        return blk_info
    
    def __verify_chain(self):
        try:
            self.__blockchain.verify_chain()
        except:
            pass
            #TODO ask peers for correct blocks
    
    def __del__(self):
        self.__network_node.stop()
