import os

class BlockchainParser():
    
    def getBlockchainLen(): return len(os.listdir('blockchain/blocks'))

    def getBlockFiles(): return sorted(os.listdir('blockchain/blocks'))