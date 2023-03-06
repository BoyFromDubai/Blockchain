from .miner import Miner
from .network_node import NetworkNode
from .wallet import Wallet
from ..blockchain import Blockchain


class Node:
    def __init__(self) -> None:
        self.blockchain = Blockchain()
        self.wallet = Wallet(self.blockchain)
        self.miner = Miner(self.blockchain, self.wallet.pk.to_string().hex())
        self.network_node = NetworkNode(self.blockchain)
        self.network_node.start()

        self.__verify_chain()

    def __update_utxos(func):
        def wrapper(*args, **kwargs):
            blk_data = func(*args, **kwargs)
            txs = args[0].blockchain.get_block_txs(blk_data)

            args[0].wallet.update_utxos(txs)

            return blk_data

        return wrapper
    
    def connect_with_bind_server(self):
        self.network_node.connect_with_bind_server()

    def create_tx(self, vouts_info, vins_info, sk):
        try:
            tx_data = self.blockchain.add_transaction(vouts_info, vins_info, sk)
            self.network_node.new_tx_msg(tx_data)
            
            return tx_data
        
        except Exception as e:
            return e
    
    def set_bind_server(self, ip, port):
        return self.network_node.set_bind_server(ip, port)

    def get_ip(self): return self.network_node.ip

    def get_peers(self): return self.network_node.get_peers()
    
    def get_chain_len(self): return self.blockchain.get_chain_len()

    def get_db_utxos(self): return self.blockchain.chainstate_db.get_utxos()

    @__update_utxos
    def mine_block(self):
        blk_info = self.miner.mine_block() 
        self.network_node.new_block_msg(blk_info)
        
        return blk_info
    
    def __verify_chain(self):
        try:
            self.blockchain.verify_chain()
        except:
            pass
            #TODO ask peers for correct blocks
    
    def __del__(self):
        self.network_node.stop()
