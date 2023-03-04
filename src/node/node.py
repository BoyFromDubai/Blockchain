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

    def __update_utxos(func):
        def wrapper(*args, **kwargs):
            blk_data = func(*args, **kwargs)
            txs = args[0].blockchain.get_block_txs(blk_data)

            args[0].wallet.update_utxos(txs)

            return blk_data

        return wrapper
    
    def connect_with_bind_server(self):
        self.network_node.connect_with_bind_server()
    
    def set_bind_server(self, ip, port):
        return self.network_node.set_bind_server(ip, port)

    def get_ip(self): return self.network_node.ip
    
    @__update_utxos
    def mine_block(self): 
        return self.miner.mine_block()
    
    def __del__(self):
        self.network_node.stop()
