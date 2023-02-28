from .miner import Miner
from .network_node import NetworkNode
from .wallet import Wallet

class Node:
    def __init__(self, blockchain, res_values) -> None:
        self.blockchain = blockchain
        self.wallet = Wallet(blockchain)
        self.miner = Miner(blockchain, self.wallet.pk.to_string().hex())

        self.res_values = res_values

    def __update_utxos(func):
        def wrapper(*args, **kwargs):
            blk_data = func(*args, **kwargs)
            txs = args[0].blockchain.get_block_txs(blk_data)

            args[0].wallet.update_utxos(txs)

            return blk_data

        return wrapper
    
    @__update_utxos
    def mine_block(self): 
        return self.miner.mine_block()
